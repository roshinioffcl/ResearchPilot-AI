const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(
  question: string,
  conversationHistory: { role: string; content: string }[]
) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      conversation_history: conversationHistory,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to get a response from ResearchPilot.");
  }

  return await response.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Document upload failed.");
  }

  return await response.json();
}

export async function getDocuments() {
  const response = await fetch(`${API_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to fetch documents.");
  }

  return await response.json();
}

export async function deleteDocument(filename: string) {
  const response = await fetch(
    `${API_URL}/documents/${encodeURIComponent(filename)}`,
    { method: "DELETE" }
  );

  if (!response.ok) {
    throw new Error("Failed to delete document.");
  }

  return await response.json();
}
