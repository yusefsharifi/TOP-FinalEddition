import React, { useState, useCallback } from "react";
import { Divider, Spin, Typography } from 'antd';
import { useConversations, useMessages, useSendMessage } from "../../api/messages";
import { ConversationList } from "./ConversationList";
import { MessageThread } from "./MessageThread";
import { MessageInput } from "./MessageInput";
import { useMessageSocket } from "../../api/messages/useMessageSocket";

// فرض: userId را از context یا auth بگیر
const userId = "1"; // به صورت داینامیک جایگزین کن

export const MessageCenter: React.FC = () => {
  const [liveMessages, setLiveMessages] = useState<Message[]>([]);

  useMessageSocket(selectedId || "", useCallback((msg: Message) => {
  setLiveMessages((prev) => [...prev, msg]);
  }, []));

  const allMessages = [...messages, ...liveMessages];

  const { data: conversations = [], isLoading: loadingConvs } = useConversations();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: messages = [], isLoading: loadingMsgs } = useMessages(selectedId || "");
  const { mutate: sendMessage, isLoading: sending } = useSendMessage(selectedId || "");

  return (
    <div>
      <ConversationList
        conversations={conversations}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />
      <Divider orientation="vertical" flexItem />
      <div>
        {loadingMsgs ? (
          <div>
            <Spin />
          </div>
        ) : selectedId ? (
          <>
            <MessageThread messages={allMessages} userId={userId} />
            <MessageInput onSend={(msg) => sendMessage(msg)} disabled={sending} />
          </>
        ) : (
          <div>
            <Typography color="text.secondary">یک گفتگو را انتخاب کنید</Typography>
          </div>
        )}
      </div>
    </div>
  );
};