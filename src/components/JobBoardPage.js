import { LitElement, html, css } from "lit";
import "@shoelace-style/shoelace/dist/components/button/button.js";
import "@shoelace-style/shoelace/dist/components/textarea/textarea.js";
import "@shoelace-style/shoelace/dist/components/alert/alert.js";

export default class JobBoardPage extends LitElement {
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
      gap: 10px;
    }

    sl-alert {
      margin-top: 15px;
    }
  `;

  showAlert(type, message) {
    const alert = document.createElement("sl-alert");
    alert.variant = type; // success, info, warning, danger
    alert.innerText = message;
    alert.open = true;

    this.shadowRoot.querySelector(".container").appendChild(alert);

    // Auto remove after 3 seconds
    setTimeout(() => {
      alert.remove();
    }, 3000);
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
          <sl-button @click=${() => this.submitJob("success")}>Submit (Success)</sl-button>
          <sl-button @click=${() => this.submitJob("info")}>Info Alert</sl-button>
          <sl-button @click=${() => this.submitJob("warning")}>Warning</sl-button>
          <sl-button @click=${() => this.submitJob("danger")}>Error</sl-button>
        </div>
      </div>
    `;
  }

  submitJob(type) {
    const textarea = this.shadowRoot.getElementById("jobInput");
    const value = textarea.value.trim();
    if (!value) {
      this.showAlert("warning", "Please enter a job posting first!");
      return;
    }

    switch (type) {
      case "success":
        this.showAlert("success", "Job posted successfully!");
        break;
      case "info":
        this.showAlert("info", "Here is some information.");
        break;
      case "warning":
        this.showAlert("warning", "This is a warning.");
        break;
      case "danger":
        this.showAlert("danger", "Something went wrong!");
        break;
    }

    // Clear textarea after success
    if (type === "success") textarea.value = "";
  }
}

customElements.define("job-board-page", JobBoardPage);