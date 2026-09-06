import { useEffect, useRef, useState } from "react";
import api from "../services/api.js";

function BellIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
      className="bi bi-bell" viewBox="0 0 16 16">
      <path d="M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2M8 1.918l-.797.161A4 4 0 0 0 4 6c0 .628-.134 2.197-.459 3.742-.16.767-.376 1.566-.663 2.258h10.244c-.287-.692-.502-1.49-.663-2.258C12.134 8.197 12 6.628 12 6a4 4 0 0 0-4-4Z" />
    </svg>
  );
}

export default function NotificationDropdown() {
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [items, setItems] = useState([]);
  const ref = useRef(null);

  const loadCount = async () => {
    try {
      const { data } = await api.get("/me/notifications/unread-count");
      setUnread(data.data.unread_count);
    } catch {
      /* ignored */
    }
  };

  useEffect(() => {
    loadCount();
    const fn = () => setOpen(false);
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) fn();
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggle = async () => {
    if (!open) {
      try {
        const { data } = await api.get("/me/notifications");
        setItems(data.data.notifications);
        setUnread(data.data.unread_count);
      } catch {
        /* ignored */
      }
    }
    setOpen((o) => !o);
  };

  const markAll = async () => {
    try {
      await api.post("/me/notifications/read-all");
      setUnread(0);
      setItems((it) => it.map((i) => ({ ...i, is_read: true })));
    } catch {
      /* ignored */
    }
  };

  const markOne = async (id) => {
    try {
      await api.post(`/me/notifications/${id}/read`);
      setUnread((u) => Math.max(0, u - 1));
      setItems((it) => it.map((i) => (i.id === id ? { ...i, is_read: true } : i)));
    } catch {
      /* ignored */
    }
  };

  return (
    <div className="position-relative" ref={ref}>
      <button className="btn btn-outline-secondary btn-sm position-relative" onClick={toggle} aria-label="Notifications">
        <BellIcon />
        {unread > 0 && (
          <span className="badge rounded-pill bg-danger position-absolute top-0 start-100 translate-middle">
            {unread}
          </span>
        )}
      </button>
      {open && (
        <div className="dropdown-menu show shadow position-absolute end-0 mt-2" style={{ width: "22rem", maxHeight: "26rem", overflowY: "auto" }}>
          <div className="d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
            <span className="fw-semibold small">Notifications</span>
            <button className="btn btn-link btn-sm p-0 text-decoration-none" onClick={markAll}>
              Mark all read
            </button>
          </div>
          {items.length === 0 && <div className="p-3 text-muted small">You are all caught up.</div>}
          {items.map((n) => (
            <button
              key={n.id}
              className={`dropdown-item text-start px-3 py-2 ${n.is_read ? "text-muted" : ""}`}
              onClick={() => markOne(n.id)}
              type="button"
            >
              <div className="small fw-semibold">{n.title}</div>
              {n.body && <div className="small">{n.body}</div>}
              <div className="small text-muted">{new Date(n.created_at).toLocaleString()}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}