from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

class FieldType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"
    IMAGE = "image"
    SIGNATURE = "signature"
    TABLE = "table"
    CHART = "chart"

class ValidationRule:
    def __init__(self, rule_type: str, value: Any, message: str):
        self.rule_type = rule_type
        self.value = value
        self.message = message

@dataclass
class FormField:
    id: str
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    default_value: Any = None
    placeholder: str = ""
    validation_rules: List[ValidationRule] = None
    options: List[Dict[str, Any]] = None
    width: int = 12
    order: int = 0
    is_visible: bool = True
    is_readonly: bool = False
    depends_on: List[str] = None
    style: Dict[str, Any] = None
    help_text: str = ""
    error_message: str = ""

class ReportFormBuilder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fields: List[FormField] = []
        self.title: str = ""
        self.description: str = ""
        self.template_id: str = ""
        self.version: str = "1.0"
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
    
    def set_title(self, title: str):
        """Set form title"""
        self.title = title
    
    def set_description(self, description: str):
        """Set form description"""
        self.description = description
    
    def set_template_id(self, template_id: str):
        """Set template ID"""
        self.template_id = template_id
    
    def add_text_field(self, 
                      id: str,
                      name: str,
                      label: str,
                      required: bool = False,
                      default_value: str = None,
                      placeholder: str = "",
                      validation_rules: List[ValidationRule] = None,
                      width: int = 12,
                      order: int = 0,
                      is_visible: bool = True,
                      is_readonly: bool = False,
                      depends_on: List[str] = None,
                      style: Dict[str, Any] = None,
                      help_text: str = "") -> FormField:
        """Add text field to form"""
        field = FormField(
            id=id,
            name=name,
            label=label,
            field_type=FieldType.TEXT,
            required=required,
            default_value=default_value,
            placeholder=placeholder,
            validation_rules=validation_rules or [],
            width=width,
            order=order,
            is_visible=is_visible,
            is_readonly=is_readonly,
            depends_on=depends_on,
            style=style,
            help_text=help_text
        )
        self.fields.append(field)
        return field
    
    def add_number_field(self,
                        id: str,
                        name: str,
                        label: str,
                        required: bool = False,
                        default_value: Union[int, float] = None,
                        min_value: Union[int, float] = None,
                        max_value: Union[int, float] = None,
                        step: Union[int, float] = 1,
                        width: int = 12,
                        order: int = 0,
                        is_visible: bool = True,
                        is_readonly: bool = False,
                        depends_on: List[str] = None,
                        style: Dict[str, Any] = None,
                        help_text: str = "") -> FormField:
        """Add number field to form"""
        validation_rules = []
        if min_value is not None:
            validation_rules.append(ValidationRule("min", min_value, f"Value must be greater than or equal to {min_value}"))
        if max_value is not None:
            validation_rules.append(ValidationRule("max", max_value, f"Value must be less than or equal to {max_value}"))
        
        field = FormField(
            id=id,
            name=name,
            label=label,
            field_type=FieldType.NUMBER,
            required=required,
            default_value=default_value,
            validation_rules=validation_rules,
            width=width,
            order=order,
            is_visible=is_visible,
            is_readonly=is_readonly,
            depends_on=depends_on,
            style=style,
            help_text=help_text
        )
        self.fields.append(field)
        return field
    
    def add_select_field(self,
                        id: str,
                        name: str,
                        label: str,
                        options: List[Dict[str, Any]],
                        required: bool = False,
                        default_value: Any = None,
                        width: int = 12,
                        order: int = 0,
                        is_visible: bool = True,
                        is_readonly: bool = False,
                        depends_on: List[str] = None,
                        style: Dict[str, Any] = None,
                        help_text: str = "") -> FormField:
        """Add select field to form"""
        field = FormField(
            id=id,
            name=name,
            label=label,
            field_type=FieldType.SELECT,
            required=required,
            default_value=default_value,
            options=options,
            width=width,
            order=order,
            is_visible=is_visible,
            is_readonly=is_readonly,
            depends_on=depends_on,
            style=style,
            help_text=help_text
        )
        self.fields.append(field)
        return field
    
    def add_table_field(self,
                       id: str,
                       name: str,
                       label: str,
                       columns: List[Dict[str, Any]],
                       required: bool = False,
                       default_value: List[Dict[str, Any]] = None,
                       min_rows: int = 0,
                       max_rows: int = None,
                       width: int = 12,
                       order: int = 0,
                       is_visible: bool = True,
                       is_readonly: bool = False,
                       depends_on: List[str] = None,
                       style: Dict[str, Any] = None,
                       help_text: str = "") -> FormField:
        """Add table field to form"""
        validation_rules = []
        if min_rows > 0:
            validation_rules.append(ValidationRule("min_rows", min_rows, f"At least {min_rows} rows are required"))
        if max_rows is not None:
            validation_rules.append(ValidationRule("max_rows", max_rows, f"Maximum {max_rows} rows are allowed"))
        
        field = FormField(
            id=id,
            name=name,
            label=label,
            field_type=FieldType.TABLE,
            required=required,
            default_value=default_value or [],
            options=columns,
            validation_rules=validation_rules,
            width=width,
            order=order,
            is_visible=is_visible,
            is_readonly=is_readonly,
            depends_on=depends_on,
            style=style,
            help_text=help_text
        )
        self.fields.append(field)
        return field
    
    def add_chart_field(self,
                       id: str,
                       name: str,
                       label: str,
                       chart_type: str,
                       data_source: Dict[str, Any],
                       required: bool = False,
                       width: int = 12,
                       order: int = 0,
                       is_visible: bool = True,
                       is_readonly: bool = False,
                       depends_on: List[str] = None,
                       style: Dict[str, Any] = None,
                       help_text: str = "") -> FormField:
        """Add chart field to form"""
        field = FormField(
            id=id,
            name=name,
            label=label,
            field_type=FieldType.CHART,
            required=required,
            options=[{
                "type": chart_type,
                "data_source": data_source
            }],
            width=width,
            order=order,
            is_visible=is_visible,
            is_readonly=is_readonly,
            depends_on=depends_on,
            style=style,
            help_text=help_text
        )
        self.fields.append(field)
        return field
    
    def add_section(self, title: str, fields: List[FormField], order: int = 0) -> Dict[str, Any]:
        """Add section to form"""
        return {
            "title": title,
            "fields": fields,
            "order": order
        }
    
    def validate_form_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate form data against field rules"""
        errors = []
        
        for field in self.fields:
            value = data.get(field.name)
            
            # Check required fields
            if field.required and value is None:
                errors.append(f"{field.label} is required")
                continue
            
            if value is not None:
                # Validate based on field type
                if field.field_type == FieldType.NUMBER:
                    try:
                        num_value = float(value)
                        for rule in field.validation_rules:
                            if rule.rule_type == "min" and num_value < rule.value:
                                errors.append(rule.message)
                            elif rule.rule_type == "max" and num_value > rule.value:
                                errors.append(rule.message)
                    except ValueError:
                        errors.append(f"{field.label} must be a number")
                
                elif field.field_type == FieldType.TABLE:
                    if not isinstance(value, list):
                        errors.append(f"{field.label} must be a list")
                    else:
                        for rule in field.validation_rules:
                            if rule.rule_type == "min_rows" and len(value) < rule.value:
                                errors.append(rule.message)
                            elif rule.rule_type == "max_rows" and len(value) > rule.value:
                                errors.append(rule.message)
        
        return len(errors) == 0, errors
    
    def get_form_schema(self) -> Dict[str, Any]:
        """Get form schema"""
        return {
            "title": self.title,
            "description": self.description,
            "template_id": self.template_id,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "fields": [
                {
                    "id": field.id,
                    "name": field.name,
                    "label": field.label,
                    "type": field.field_type.value,
                    "required": field.required,
                    "default_value": field.default_value,
                    "placeholder": field.placeholder,
                    "validation_rules": [
                        {
                            "type": rule.rule_type,
                            "value": rule.value,
                            "message": rule.message
                        }
                        for rule in (field.validation_rules or [])
                    ],
                    "options": field.options,
                    "width": field.width,
                    "order": field.order,
                    "is_visible": field.is_visible,
                    "is_readonly": field.is_readonly,
                    "depends_on": field.depends_on,
                    "style": field.style,
                    "help_text": field.help_text
                }
                for field in sorted(self.fields, key=lambda x: x.order)
            ]
        }
    
    def save_form(self, file_path: str):
        """Save form to file"""
        try:
            schema = self.get_form_schema()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Form saved successfully to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving form: {str(e)}")
            raise
    
    @classmethod
    def load_form(cls, file_path: str) -> 'ReportFormBuilder':
        """Load form from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            builder = cls()
            builder.title = schema["title"]
            builder.description = schema["description"]
            builder.template_id = schema["template_id"]
            builder.version = schema["version"]
            builder.created_at = datetime.fromisoformat(schema["created_at"])
            builder.updated_at = datetime.fromisoformat(schema["updated_at"])
            
            for field_data in schema["fields"]:
                field = FormField(
                    id=field_data["id"],
                    name=field_data["name"],
                    label=field_data["label"],
                    field_type=FieldType(field_data["type"]),
                    required=field_data["required"],
                    default_value=field_data["default_value"],
                    placeholder=field_data["placeholder"],
                    validation_rules=[
                        ValidationRule(rule["type"], rule["value"], rule["message"])
                        for rule in field_data["validation_rules"]
                    ],
                    options=field_data["options"],
                    width=field_data["width"],
                    order=field_data["order"],
                    is_visible=field_data["is_visible"],
                    is_readonly=field_data["is_readonly"],
                    depends_on=field_data["depends_on"],
                    style=field_data["style"],
                    help_text=field_data["help_text"]
                )
                builder.fields.append(field)
            
            return builder
        except Exception as e:
            logging.error(f"Error loading form: {str(e)}")
            raise

class ReportGenerator(ABC):
    @abstractmethod
    def generate_report(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report from form data"""
        pass

class PDFReportGenerator(ReportGenerator):
    def __init__(self, form_builder: ReportFormBuilder):
        self.form_builder = form_builder
    
    def generate_report(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF report from form data"""
        # Implementation for PDF report generation
        pass

class ExcelReportGenerator(ReportGenerator):
    def __init__(self, form_builder: ReportFormBuilder):
        self.form_builder = form_builder
    
    def generate_report(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Excel report from form data"""
        # Implementation for Excel report generation
        pass

class ChartReportGenerator(ReportGenerator):
    def __init__(self, form_builder: ReportFormBuilder):
        self.form_builder = form_builder
    
    def generate_report(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart report from form data"""
        # Implementation for chart report generation
        pass 