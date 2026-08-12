import { useSelector, useDispatch } from "react-redux";
import { updateField, resetForm } from "../redux/complaintSlice";
import { saveComplaint } from "../api";

const placeholder = (v) => (v ? v : "Awaiting AI extraction...");

function Field({ label, field, type = "text", options }) {
  const dispatch = useDispatch();
  const value = useSelector((s) => s.complaint.form[field]);

  return (
    <div className="field">
      <label>{label}</label>
      {options ? (
        <select
          value={value}
          onChange={(e) => dispatch(updateField({ field, value: e.target.value }))}
        >
          <option value="">{placeholder()}</option>
          {options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          placeholder="Awaiting AI extraction..."
          onChange={(e) => dispatch(updateField({ field, value: e.target.value }))}
        />
      )}
    </div>
  );
}

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const form = useSelector((s) => s.complaint.form);
  const aiRisk = useSelector((s) => s.complaint.form.ai_risk_level);

  const handleSave = async () => {
    try {
      await saveComplaint(form);
      alert("Complaint saved successfully.");
    } catch (err) {
      alert("Failed to save complaint: " + err.message);
    }
  };

  return (
    <div className="panel form-panel">
      <div className="panel-header">
        <div>
          <h2>Log Customer Complaint</h2>
          <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <span className="badge">Pending Triage</span>
      </div>

      <section>
        <h3>1. Origin &amp; Customer Details</h3>
        <div className="grid-2">
          <Field label="Complaint Source" field="complaint_source"
            options={["Email", "Phone Call", "Customer Portal", "Regulatory Authority"]} />
          <Field label="Customer Name" field="customer_name" />
        </div>
      </section>

      <section>
        <h3>2. Product &amp; Batch Identification</h3>
        <div className="grid-2">
          <Field label="Product Name" field="product_name" />
          <Field label="Product Strength/Grade" field="product_strength_grade" />
          <Field label="Batch/Lot Number" field="batch_lot_number" />
          <Field label="Manufacturing Date" field="manufacturing_date" type="date" />
          <Field label="Expiry Date" field="expiry_date" type="date" />
          <Field label="Quantity Affected (kg)" field="quantity_affected" type="number" />
        </div>
      </section>

      <section>
        <h3>3. Complaint Details</h3>
        <div className="grid-2">
          <Field label="Complaint Type" field="complaint_type"
            options={["Discoloration", "Contamination", "Packaging Defect", "Mislabeling", "Potency Deviation", "Other"]} />
          <Field label="Complaint Date" field="complaint_date" type="date" />
        </div>
        <div className="field">
          <label>Detailed Complaint Description</label>
          <textarea
            rows={4}
            value={form.detailed_complaint_description}
            placeholder="Awaiting AI extraction..."
            onChange={(e) => dispatch(updateField({ field: "detailed_complaint_description", value: e.target.value }))}
          />
        </div>
      </section>

      <section>
        <h3>4. Initial Assessment &amp; Priority</h3>
        <div className="grid-2">
          <Field label="Initial Severity" field="initial_severity" options={["Critical", "Major", "Minor"]} />
          <Field label="Priority" field="priority" options={["High", "Medium", "Low"]} />
        </div>
      </section>

      {aiRisk && (
        <section className="ai-risk-box">
          <h3>AI Copilot Risk Assessment</h3>
          <p><strong>Risk Level:</strong> {form.ai_risk_level}</p>
          <p className="rationale">{form.ai_risk_rationale}</p>
        </section>
      )}

      <div className="actions">
        <button className="btn-secondary" onClick={() => dispatch(resetForm())}>Reset Form</button>
        <button className="btn-primary" onClick={handleSave}>Save Complaint</button>
      </div>
    </div>
  );
}
