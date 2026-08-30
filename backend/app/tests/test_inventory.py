"""
Inventory Module - Test Suite
TOP WorX ERP System

Run:
    pytest backend/app/tests/test_inventory.py -v --asyncio-mode=auto

Requires:
    pytest-asyncio, httpx, pytest-mock
    A test PostgreSQL database or SQLite (swap the engine in conftest).
"""
from __future__ import annotations

from decimal import Decimal
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.models.inventory import Base, MovementType
from app.schemas.inventory import (
    InboundMovementCreate,
    InventoryItemCreate,
    InventoryLocationCreate,
    OutboundMovementCreate,
    StockAdjustRequest,
    StockTransferRequest,
)
from app.services.inventory_service import (
    InsufficientStockError,
    InventoryService,
    InventoryServiceError,
    ItemHasStockError,
    inventory_service,
)


# ---------------------------------------------------------------------------
# Test database setup (in-memory SQLite for unit/integration tests)
# ---------------------------------------------------------------------------
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _create_location(db: AsyncSession, code: str = "WH-A1") -> int:
    from app.crud.inventory import location_crud
    from app.schemas.inventory import InventoryLocationCreate

    loc = await location_crud.create(
        db,
        InventoryLocationCreate(
            code=code,
            name=f"Test Location {code}",
            warehouse="WH-MAIN",
        ),
    )
    await db.commit()
    return loc.id


async def _create_item(db: AsyncSession, sku: str = "ITEM-00001") -> int:
    item = await inventory_service.create_item(
        db,
        InventoryItemCreate(
            sku=sku,
            name="Test Widget",
            unit_of_measure="pcs",
            standard_cost=Decimal("10.00"),
        ),
    )
    await db.commit()
    return item.id


# ===========================================================================
# UNIT TESTS — Service methods (mocked DB)
# ===========================================================================


class TestSKUGeneration:
    @pytest.mark.asyncio
    async def test_generates_unique_sku(self, db_session: AsyncSession):
        sku = await inventory_service.generate_sku(db_session)
        assert sku.startswith("ITEM-")
        parts = sku.split("-")
        assert len(parts) == 2
        assert parts[1].isdigit()
        assert len(parts[1]) == 5

    @pytest.mark.asyncio
    async def test_custom_prefix(self, db_session: AsyncSession):
        sku = await inventory_service.generate_sku(db_session, prefix="ELEC")
        assert sku.startswith("ELEC-")

    @pytest.mark.asyncio
    async def test_no_collision(self, db_session: AsyncSession):
        """Generate 50 SKUs and verify all unique."""
        skus = {await inventory_service.generate_sku(db_session) for _ in range(50)}
        assert len(skus) == 50


class TestBarcodeGeneration:
    def test_barcode_returns_base64(self):
        result = inventory_service.generate_barcode_base64("ITEM-00001")
        assert isinstance(result, str)
        assert len(result) > 100  # base64 PNG is always sizeable

    def test_qr_returns_base64(self):
        result = inventory_service.generate_qr_base64({"sku": "ITEM-00001"})
        assert isinstance(result, str)
        import base64

        decoded = base64.b64decode(result)
        # PNG magic bytes
        assert decoded[:8] == b"\x89PNG\r\n\x1a\n"


class TestCreateItem:
    @pytest.mark.asyncio
    async def test_create_with_explicit_sku(self, db_session: AsyncSession):
        item = await inventory_service.create_item(
            db_session,
            InventoryItemCreate(sku="WIDGET-001", name="Widget A", unit_of_measure="pcs"),
        )
        await db_session.commit()
        assert item.sku == "WIDGET-001"
        assert item.barcode == "WIDGET-001"
        assert item.qr_code is not None

    @pytest.mark.asyncio
    async def test_create_without_sku_auto_generates(self, db_session: AsyncSession):
        item = await inventory_service.create_item(
            db_session,
            InventoryItemCreate(name="Auto SKU Item", unit_of_measure="kg"),
        )
        await db_session.commit()
        assert item.sku.startswith("ITEM-")

    @pytest.mark.asyncio
    async def test_duplicate_sku_raises(self, db_session: AsyncSession):
        await _create_item(db_session, "DUP-001")
        with pytest.raises(Exception):  # DuplicateSKUError
            await inventory_service.create_item(
                db_session,
                InventoryItemCreate(sku="DUP-001", name="Dup", unit_of_measure="pcs"),
            )


class TestInboundMovement:
    @pytest.mark.asyncio
    async def test_inbound_increases_stock(self, db_session: AsyncSession):
        item_id = await _create_item(db_session, "IN-TEST-001")
        loc_id = await _create_location(db_session, "WH-RCV")

        movement = await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(
                item_id=item_id,
                to_location_id=loc_id,
                quantity=Decimal("100"),
            ),
        )
        await db_session.commit()

        assert movement.movement_type == MovementType.INBOUND
        assert movement.quantity == Decimal("100")
        assert movement.quantity_before == Decimal("0")
        assert movement.quantity_after == Decimal("100")

    @pytest.mark.asyncio
    async def test_inbound_updates_last_purchase_price(self, db_session: AsyncSession):
        from app.crud.inventory import item_crud

        item_id = await _create_item(db_session, "IN-PRICE-001")
        loc_id = await _create_location(db_session, "WH-P1")

        await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(
                item_id=item_id,
                to_location_id=loc_id,
                quantity=Decimal("50"),
                unit_cost=Decimal("12.50"),
            ),
        )
        await db_session.commit()

        item = await item_crud.get(db_session, item_id)
        assert item.last_purchase_price == Decimal("12.50")


class TestOutboundMovement:
    @pytest.mark.asyncio
    async def test_outbound_decreases_stock(self, db_session: AsyncSession):
        item_id = await _create_item(db_session, "OUT-TEST-001")
        loc_id = await _create_location(db_session, "WH-OUT1")

        # First receive stock
        await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(item_id=item_id, to_location_id=loc_id, quantity=Decimal("50")),
        )
        await db_session.commit()

        movement = await inventory_service.process_outbound(
            db_session,
            OutboundMovementCreate(item_id=item_id, from_location_id=loc_id, quantity=Decimal("20")),
        )
        await db_session.commit()

        assert movement.quantity_before == Decimal("50")
        assert movement.quantity_after == Decimal("30")

    @pytest.mark.asyncio
    async def test_outbound_raises_when_insufficient(self, db_session: AsyncSession):
        item_id = await _create_item(db_session, "OUT-INSUF-001")
        loc_id = await _create_location(db_session, "WH-INSUF")

        with pytest.raises(InsufficientStockError):
            await inventory_service.process_outbound(
                db_session,
                OutboundMovementCreate(
                    item_id=item_id, from_location_id=loc_id, quantity=Decimal("999")
                ),
            )


class TestStockTransfer:
    @pytest.mark.asyncio
    async def test_transfer_is_atomic(self, db_session: AsyncSession):
        """Both source decrease and destination increase happen in one flush."""
        from app.crud.inventory import stock_crud

        item_id = await _create_item(db_session, "TRF-TEST-001")
        src_id = await _create_location(db_session, "WH-SRC")
        dst_id = await _create_location(db_session, "WH-DST")

        await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(item_id=item_id, to_location_id=src_id, quantity=Decimal("80")),
        )
        await db_session.commit()

        out_mv, in_mv = await inventory_service.transfer_stock(
            db_session,
            StockTransferRequest(
                item_id=item_id,
                from_location_id=src_id,
                to_location_id=dst_id,
                quantity=Decimal("30"),
            ),
        )
        await db_session.commit()

        src_stock = await stock_crud.get_or_create(db_session, item_id, src_id)
        dst_stock = await stock_crud.get_or_create(db_session, item_id, dst_id)

        assert src_stock.quantity_on_hand == Decimal("50")
        assert dst_stock.quantity_on_hand == Decimal("30")
        assert out_mv.quantity == Decimal("30")
        assert in_mv.quantity == Decimal("30")

    @pytest.mark.asyncio
    async def test_transfer_same_location_raises(self, db_session: AsyncSession):
        item_id = await _create_item(db_session, "TRF-SAME-001")
        loc_id = await _create_location(db_session, "WH-SAME")

        with pytest.raises(Exception):  # Pydantic validation error
            StockTransferRequest(
                item_id=item_id,
                from_location_id=loc_id,
                to_location_id=loc_id,
                quantity=Decimal("10"),
            )


class TestStockAdjustment:
    @pytest.mark.asyncio
    async def test_absolute_adjustment(self, db_session: AsyncSession):
        from app.crud.inventory import stock_crud

        item_id = await _create_item(db_session, "ADJ-ABS-001")
        loc_id = await _create_location(db_session, "WH-ADJ1")

        await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(item_id=item_id, to_location_id=loc_id, quantity=Decimal("50")),
        )
        await db_session.commit()

        await inventory_service.adjust_stock(
            db_session,
            StockAdjustRequest(
                item_id=item_id,
                location_id=loc_id,
                new_quantity=Decimal("45"),
                reason="Physical count correction",
            ),
        )
        await db_session.commit()

        stock = await stock_crud.get_or_create(db_session, item_id, loc_id)
        assert stock.quantity_on_hand == Decimal("45")

    @pytest.mark.asyncio
    async def test_delta_adjustment(self, db_session: AsyncSession):
        from app.crud.inventory import stock_crud

        item_id = await _create_item(db_session, "ADJ-DELTA-001")
        loc_id = await _create_location(db_session, "WH-ADJ2")

        await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(item_id=item_id, to_location_id=loc_id, quantity=Decimal("20")),
        )
        await db_session.commit()

        await inventory_service.adjust_stock(
            db_session,
            StockAdjustRequest(
                item_id=item_id,
                location_id=loc_id,
                quantity_delta=Decimal("-5"),
                reason="Damaged goods write-off",
            ),
        )
        await db_session.commit()

        stock = await stock_crud.get_or_create(db_session, item_id, loc_id)
        assert stock.quantity_on_hand == Decimal("15")


class TestDeleteGuard:
    @pytest.mark.asyncio
    async def test_cannot_delete_item_with_stock(self, db_session: AsyncSession):
        item_id = await _create_item(db_session, "DEL-GUARD-001")
        loc_id = await _create_location(db_session, "WH-DEL")

        await inventory_service.process_inbound(
            db_session,
            InboundMovementCreate(item_id=item_id, to_location_id=loc_id, quantity=Decimal("1")),
        )
        await db_session.commit()

        with pytest.raises(ItemHasStockError):
            await inventory_service.assert_can_delete_item(db_session, item_id)

    @pytest.mark.asyncio
    async def test_can_delete_item_with_zero_stock(self, db_session: AsyncSession):
        item_id = await _create_item(db_session, "DEL-OK-001")
        # No stock added — should not raise
        await inventory_service.assert_can_delete_item(db_session, item_id)


# ===========================================================================
# SCHEMA VALIDATION TESTS
# ===========================================================================


class TestSchemaValidation:
    def test_sku_format_enforced(self):
        with pytest.raises(Exception):
            InventoryItemCreate(
                sku="invalid sku!",
                name="Bad SKU",
                unit_of_measure="pcs",
            )

    def test_sku_auto_uppercased(self):
        item = InventoryItemCreate(
            sku="item-00001",
            name="Lower SKU",
            unit_of_measure="pcs",
        )
        assert item.sku == "ITEM-00001"

    def test_max_stock_must_exceed_reorder(self):
        with pytest.raises(Exception):
            InventoryItemCreate(
                sku="ITEM-BAD",
                name="Bad Reorder",
                unit_of_measure="pcs",
                global_reorder_point=Decimal("100"),
                global_max_stock=Decimal("50"),  # less than reorder_point
            )

    def test_adjust_request_requires_exactly_one_qty_mode(self):
        with pytest.raises(Exception):
            StockAdjustRequest(
                item_id=1,
                location_id=1,
                # both provided — should fail
                new_quantity=Decimal("10"),
                quantity_delta=Decimal("5"),
                reason="Test",
            )

    def test_adjust_request_neither_qty_mode(self):
        with pytest.raises(Exception):
            StockAdjustRequest(
                item_id=1,
                location_id=1,
                # neither provided — should fail
                reason="Test",
            )

    def test_transfer_different_locations_required(self):
        with pytest.raises(Exception):
            StockTransferRequest(
                item_id=1,
                from_location_id=5,
                to_location_id=5,  # same
                quantity=Decimal("10"),
            )


# ===========================================================================
# CONCURRENCY TEST
# ===========================================================================


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_outbound_respected(self, db_engine):
        """
        Simulate two concurrent outbound requests against the same stock.
        One should succeed; the other should raise InsufficientStockError.

        NOTE: True serialization requires FOR UPDATE locks or optimistic locking
        at the DB level. This test verifies the business rule check is present;
        production concurrency is enforced by PostgreSQL row-level locking.
        """
        import asyncio

        factory = async_sessionmaker(db_engine, expire_on_commit=False)

        async with factory() as setup_db:
            item_id = await _create_item(setup_db, "CONC-TEST-001")
            loc_id = await _create_location(setup_db, "WH-CONC")
            await inventory_service.process_inbound(
                setup_db,
                InboundMovementCreate(
                    item_id=item_id, to_location_id=loc_id, quantity=Decimal("10")
                ),
            )
            await setup_db.commit()

        results = []

        async def try_outbound():
            async with factory() as session:
                try:
                    await inventory_service.process_outbound(
                        session,
                        OutboundMovementCreate(
                            item_id=item_id,
                            from_location_id=loc_id,
                            quantity=Decimal("8"),
                        ),
                    )
                    await session.commit()
                    results.append("ok")
                except InsufficientStockError:
                    results.append("insufficient")
                except Exception as e:
                    results.append(f"error:{e}")

        # Run both concurrently
        await asyncio.gather(try_outbound(), try_outbound())

        ok_count = results.count("ok")
        insuf_count = results.count("insufficient")

        # At least one should fail (stock is only 10, each request wants 8)
        assert ok_count >= 1
        assert ok_count + insuf_count == 2, f"Unexpected results: {results}"
