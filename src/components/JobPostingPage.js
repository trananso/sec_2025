import { LitElement, html, css } from "lit";
import "@shoelace-style/shoelace/dist/components/button/button.js";
import "@shoelace-style/shoelace/dist/components/textarea/textarea.js";
import "@shoelace-style/shoelace/dist/components/alert/alert.js";

export default class JobPostingPage extends LitElement {
  static styles = css`
    :host {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background-color: var(--sl-color-neutral-100);
      font-family: var(--sl-font-sans);
      box-sizing: border-box;
    }

    .container {
      max-width: 600px;
      width: 100%;
      padding: 20px;
      text-align: center;
    }

    h1 {
      margin-bottom: 20px;
      font-size: 2.5rem;
      color: var(--sl-color-primary-600);
    }

    sl-textarea {
      width: 100%;
      min-height: 200px;
      margin-bottom: 15px;
    }

    .actions {
      display: flex;
      justify-content: center;
      margin-bottom: 15px;
    }

    sl-alert {
      margin-top: 10px;
      text-align: left;
    }
  `;

  static properties = {
    flags: { type: Array },
  };

  constructor() {
    super();
    this.flags = [];
  }

  analyzeJobPosting(text) {
    return [
      { id: "length", message: "Job posting is very short.", active: text.length < 50 },
      { id: "missingSalary", message: "No salary information provided.", active: !text.includes("$") },
      { id: "missingLocation", message: "No location specified.", active: !text.toLowerCase().includes("location") },
    ];
  }

  runAnalysis() {
    const textarea = this.shadowRoot.getElementById("jobInput");
    const text = textarea.value.trim();

    const results = this.analyzeJobPosting(text);
    // Keep only active flags
    this.flags = results.filter(f => f.active);
  }

  render() {
    return html`
      <div class="container">
        <h1>Job Board</h1>

        <sl-textarea
          placeholder="Enter job posting here…"
          resize="auto"
          id="jobInput"
        ></sl-textarea>

        <div class="actions">
          <sl-button variant="primary" @click=${this.runAnalysis}>
            Analyze Job Posting
          </sl-button>
        </div>

        <!-- Display alerts for active flags -->
        ${this.flags.map(
          flag => html`<sl-alert variant="warning" open>${flag.message}</sl-alert>`
        )}
      </div>
    `;
  }
}

customElements.define("job-posting-page", JobPostingPage);