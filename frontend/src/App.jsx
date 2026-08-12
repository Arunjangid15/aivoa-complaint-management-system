import ComplaintForm from "./components/ComplaintForm";
import AIAssistant from "./components/AIAssistant";
import "./index.css";

export default function App() {
  return (
    <div className="app-shell">
      <div className="two-panel">
        <ComplaintForm />
        <AIAssistant />
      </div>
    </div>
  );
}
