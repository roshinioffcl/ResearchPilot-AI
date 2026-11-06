
import { useEffect, useState } from "react";
import { sendMessage, uploadDocument, getDocuments, deleteDocument } from "./services/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: { document: string; page: number }[];
};

type DocumentInfo = {
  pages: number;
  chunks: number;
  indexed_at: string;
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [documents, setDocuments] = useState<Record<string, DocumentInfo>>({});
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function refreshDocuments() {
    const data = await getDocuments();
    setDocuments(data);
  }

  useEffect(() => {
    refreshDocuments().catch(() => {
      setError("Couldn't load your documents.");
    });
  }, []);

  async function handleSend() {
    const text = question.trim();
    if (!text || loading) return;

    const updatedMessages: Message[] = [
      ...messages,
      { role: "user", content: text },
    ];

    setMessages(updatedMessages);
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const history = messages.map(({ role, content }) => ({
        role,
        content,
      }));

      const data = await sendMessage(text, history);

      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch {
      setError("Couldn't connect to ResearchPilot. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const result = await uploadDocument(file);
      await refreshDocuments();
      alert(`${result.document} uploaded and indexed successfully!`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleDelete(filename: string) {
    if (!window.confirm(`Delete ${filename}?`)) return;

    setError("");

    try {
      await deleteDocument(filename);
      await refreshDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed.");
    }
  }

  return (
    <div className="flex h-screen bg-[#0b0d12] text-white">
      <aside className="flex w-80 shrink-0 flex-col border-r border-white/10 p-5">
        <h1 className="text-xl font-bold tracking-tight">
          🔬 ResearchPilot <span className="text-violet-400">AI</span>
        </h1>

        <button
          onClick={() => {
            setMessages([]);
            setError("");
          }}
          className="mt-8 w-full rounded-xl bg-violet-600 p-3 text-sm font-medium hover:bg-violet-500"
        >
          + New Chat
        </button>

        <div className="mt-8 flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            My Documents ({Object.keys(documents).length})
          </p>

          <label className="cursor-pointer rounded-lg bg-violet-600 px-3 py-2 text-xs hover:bg-violet-500">
            {uploading ? "Uploading..." : "+ Upload"}
            <input
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              disabled={uploading}
              onChange={handleUpload}
            />
          </label>
        </div>

        <div className="mt-4 flex-1 space-y-2 overflow-y-auto">
          {Object.entries(documents).length === 0 ? (
            <p className="text-xs text-gray-500">
              No documents uploaded yet.
            </p>
          ) : (
            Object.entries(documents).map(([filename, info]) => (
              <div
                key={filename}
                className="rounded-xl border border-white/10 bg-white/[0.03] p-3"
              >
                <p className="break-words text-sm font-medium text-gray-200">
                  📄 {filename}
                </p>
                <p className="mt-2 text-xs text-gray-500">
                  {info.pages} pages · {info.chunks} chunks
                </p>
                <button
                  onClick={() => handleDelete(filename)}
                  className="mt-2 text-xs text-red-400 hover:text-red-300"
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>

        <div className="border-t border-white/10 pt-4">
          <p className="text-xs text-gray-500">ResearchPilot AI · v1.0</p>
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-white/10 px-8">
          <span className="text-sm text-gray-400">Research Workspace</span>
          <span className="rounded-full border border-green-500/20 bg-green-500/10 px-3 py-1 text-xs text-green-400">
            ● System Ready
          </span>
        </header>

        <section className="flex-1 space-y-5 overflow-y-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center">
              <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-600/15 text-3xl">
                🔬
              </div>
              <h2 className="text-3xl font-semibold">Welcome to ResearchPilot</h2>
              <p className="mt-3 max-w-lg text-center text-sm leading-6 text-gray-400">
                Your AI-powered research assistant. Ask questions about your
                indexed documents and get answers grounded in your sources.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`mx-auto max-w-3xl rounded-2xl p-5 ${
                  message.role === "user"
                    ? "bg-violet-600/15"
                    : "border border-white/10 bg-white/[0.03]"
                }`}
              >
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
                  {message.role === "user" ? "You" : "ResearchPilot AI"}
                </p>

                <p className="whitespace-pre-wrap text-sm leading-7 text-gray-200">
                  {message.content}
                </p>
              </div>
            ))
          )}

          {loading && (
            <p className="mx-auto max-w-3xl text-sm text-violet-300">
              ResearchPilot is thinking...
            </p>
          )}

          {error && (
            <p className="mx-auto max-w-3xl text-sm text-red-400">{error}</p>
          )}
        </section>

        <div className="mx-auto w-full max-w-3xl px-6 pb-8">
          <div className="flex items-end gap-3 rounded-2xl border border-white/10 bg-[#151821] p-3">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask ResearchPilot about your documents..."
              rows={2}
              className="flex-1 resize-none bg-transparent p-2 text-sm text-white outline-none placeholder:text-gray-500"
            />

            <button
              onClick={handleSend}
              disabled={loading || !question.trim()}
              className="rounded-xl bg-violet-600 px-5 py-3 text-sm font-medium hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {loading ? "..." : "Send ↑"}
            </button>
          </div>

          <p className="mt-3 text-center text-xs text-gray-600">
            ResearchPilot AI can make mistakes. Verify important information.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
