import { useRef, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import {
  populateFromExtraction,
  setExtractionProgress,
  setExtractionStatus,
  addChatMessage,
} from "../redux/complaintSlice";
import { extractFromFile, extractFromText, chatWithAssistant } from "../api";

export default function AIAssistant() {
  const dispatch = useDispatch();
  const fileInputRef = useRef(null);
  const [pasteText, setPasteText] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const progress = useSelector((s) => s.complaint.extractionProgress);
  const status = useSelector((s) => s.complaint.extractionStatus);
  const messages = useSelector((s) => s.complaint.chatMessages);
  const form = useSelector((s) => s.complaint.form);

  // Simulated progressive bar while the real request is in flight —
  // gives the UI feedback the reference screenshot shows ("10%", "Analyzing...")
  const runWithProgress = async (task) => {
    dispatch(setExtractionStatus("extracting"));
    let current = 10;
    dispatch(setExtractionProgress(current));
    const tick = setInterval(() => {
      current = Math.min(current + 15, 85);
      dispatch(setExtractionProgress(current));
    }, 400);
    try {
      const result = await task();
      clearInterval(tick);
      dispatch(setExtractionProgress(100));
      dispatch(populateFromExtraction(result));
      dispatch(setExtractionStatus("done"));
      dispatch(addChatMessage({
        role: "assistant",
        text: "I've extracted the complaint details and populated the form. Please review before saving.",
      }));
    } catch (err) {
      clearInterval(tick);
      dispatch(setExtractionStatus("error"));
      dispatch(addChatMessage({ role: "assistant", text: `Extraction failed: ${err.message}` }));
    }
  };

  const handleFile = (file) => {
    if (!file) return;
    runWithProgress(() => extractFromFile(file));
  };

  const handlePasteSubmit = () => {
    if (!pasteText.trim()) return;
    runWithProgress(() => extractFromText(pasteText));
  };

  const handleChatSend = async () => {
    if (!chatInput.trim()) return;
    dispatch(addChatMessage({ role: "user", text: chatInput }));
    const msg = chatInput;
    setChatInput("");
    const { reply } = await chatWithAssistant(msg, form);
    dispatch(addChatMessage({ role: "assistant", text: reply }));
  };

  return (
    <div className="panel assistant-panel">
      <div className="panel-header">
        <h2>✨ AI Complaint Intake Assistant</h2>
        <span className="badge beta">BETA</span>
      </div>

      <div
        className={`dropzone ${dragOver ? "dragover" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFile(e.dataTransfer.files[0]);
        }}
        onClick={() => fileInputRef.current.click()}
      >
        <p>⬆ Drag &amp; drop complaint document here</p>
        <p className="link">or click to browse</p>
        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept=".pdf,.docx,.txt,.eml"
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      <div className="or-divider">OR</div>

      <textarea
        className="paste-box"
        placeholder="Paste Complaint Text / Email"
        rows={3}
        value={pasteText}
        onChange={(e) => setPasteText(e.target.value)}
      />
      <button className="btn-primary full-width" onClick={handlePasteSubmit}>
        Extract from Pasted Text
      </button>

      <p className="hint">ⓘ Supported formats: PDF, DOCX, TXT, EML · Max file size: 10MB</p>

      {status === "extracting" && (
        <div className="progress-section">
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
          <p>{progress}%</p>
          <p className="dim">Analyzing document content and extracting key details...<br />Please wait, this may take a few moments.</p>
        </div>
      )}

      <div className="chat-section">
        <h4>AI ASSISTANT</h4>
        <div className="chat-log">
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role}`}>{m.text}</div>
          ))}
        </div>
        <div className="chat-input-row">
          <input
            placeholder="Ask me anything about this complaint..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleChatSend()}
          />
          <button onClick={handleChatSend}>➤</button>
        </div>
        <p className="disclaimer">AI responses may contain errors. Please verify information.</p>
      </div>
    </div>
  );
}
