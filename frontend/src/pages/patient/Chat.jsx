import { useEffect, useRef, useState } from "react";
import api from "../../services/api.js";
import AppLayout from "../../layouts/AppLayout.jsx";

export default function Chat() {
  const [sessions, setSessions] = useState([]);
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const bottomRef = useRef(null);

  const loadSessions = async () => {
    const { data } = await api.get("/patients/chat/sessions");
    setSessions(data.data.sessions);
  };

  useEffect(() => {
    loadSessions().catch(() => {});
  }, []);

  useEffect(() => {
    if (active) {
      api
        .get(`/patients/chat/sessions/${active}`)
        .then(({ data }) => {
          setMessages(data.data.session.messages || []);
          setExpanded(false);
        })
        .catch(() => {});
    }
  }, [active]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  const newSession = async () => {
    const { data } = await api.post("/patients/chat/sessions");
    setActive(data.data.session.id);
    loadSessions();
  };

  const send = async () => {
    const content = input.trim();
    if (!content || sending) return;
    setSending(true);
    try {
      const { data } = await api.post(`/patients/chat/sessions/${active}/messages`, { content });
      setMessages((m) => [...m, data.data.user_message, data.data.bot_message]);
      setInput("");
      loadSessions();
    } catch (err) {
      setMessages((m) => [
        ...m,
        { id: "err", sender: "BOT", content: err.response?.data?.message || "Something went wrong." },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <AppLayout>
      <div className="container" style={{ maxWidth: "60rem" }}>
        <h1 className="h3 mb-4">AYUConnect Assistant</h1>

        <div className="row g-3">
          <div className="col-md-4">
            <div className="card">
              <div className="card-body">
                <button className="btn btn-primary btn-sm w-100 mb-3" onClick={newSession}>
                  New conversation
                </button>
                <div className="list-group">
                  {sessions.map((s) => (
                    <button
                      key={s.id}
                      className={`list-group-item list-group-item-action ${active === s.id ? "active" : ""}`}
                      onClick={() => setActive(s.id)}
                    >
                      <div className="small fw-semibold text-truncate">{s.title}</div>
                      <div className="small text-muted">{new Date(s.updated_at).toLocaleDateString()}</div>
                    </button>
                  ))}
                  {sessions.length === 0 && <div className="text-muted small">No conversations yet.</div>}
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-8">
            <div className="card">
              <div className="card-body" style={{ height: "26rem", overflowY: "auto" }}>
                {!active && <div className="text-muted text-center mt-5">Start a conversation to ask about AYUSH care.</div>}
                {active && messages.length === 0 && (
                  <div className="text-muted text-center mt-5">Say hello to begin.</div>
                )}
                {messages.map((m, i) => (
                  <div
                    key={m.id || i}
                    className={`d-flex mb-2 ${m.sender === "USER" ? "justify-content-end" : "justify-content-start"}`}
                  >
                    <div
                      className={`rounded-3 px-3 py-2 small ${m.sender === "USER" ? "bg-primary text-white" : "bg-light border"}`}
                      style={{ maxWidth: "80%" }}
                    >
                      {m.content}
                    </div>
                  </div>
                ))}
                {sending && <div className="text-muted small">Assistant is typing…</div>}
                <div ref={bottomRef} />
              </div>
              {expanded === true && null}
              <div className="card-footer d-flex gap-2">
                <input
                  className="form-control"
                  placeholder={active ? "Type a message…" : "Create a conversation first"}
                  value={input}
                  disabled={!active || sending}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && send()}
                />
                <button className="btn btn-primary" disabled={!active || sending || !input.trim()} onClick={send}>
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}