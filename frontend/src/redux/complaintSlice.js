import { createSlice } from "@reduxjs/toolkit";

const emptyForm = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength_grade: "",
  batch_lot_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: "",
  complaint_type: "",
  complaint_date: "",
  detailed_complaint_description: "",
  initial_severity: "",
  priority: "",
  ai_risk_level: "",
  ai_risk_rationale: "",
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState: {
    form: emptyForm,
    extractionProgress: 0,   // 0-100, drives the progress bar
    extractionStatus: "idle", // idle | extracting | done | error
    chatMessages: [
      {
        role: "assistant",
        text: "Upload a complaint document or paste text above. I will automatically extract the details and populate the form for you.",
      },
    ],
  },
  reducers: {
    updateField(state, action) {
      const { field, value } = action.payload;
      state.form[field] = value;
    },
    populateFromExtraction(state, action) {
      // Merge AI-extracted fields into the form, keeping nulls as blanks
      const extracted = action.payload;
      Object.keys(emptyForm).forEach((key) => {
        if (extracted[key] !== undefined && extracted[key] !== null) {
          state.form[key] = extracted[key];
        }
      });
    },
    setExtractionProgress(state, action) {
      state.extractionProgress = action.payload;
    },
    setExtractionStatus(state, action) {
      state.extractionStatus = action.payload;
    },
    addChatMessage(state, action) {
      state.chatMessages.push(action.payload);
    },
    resetForm(state) {
      state.form = emptyForm;
      state.extractionProgress = 0;
      state.extractionStatus = "idle";
    },
  },
});

export const {
  updateField,
  populateFromExtraction,
  setExtractionProgress,
  setExtractionStatus,
  addChatMessage,
  resetForm,
} = complaintSlice.actions;

export default complaintSlice.reducer;
