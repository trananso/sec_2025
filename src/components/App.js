import { LitElement, html, css } from "lit";
import "@shoelace-style/shoelace/dist/components/textarea/textarea.js";
import "@shoelace-style/shoelace/dist/components/button/button.js";
import "@shoelace-style/shoelace/dist/components/card/card.js";

export default class App extends LitElement {
  static styles = css`
    :host {
      display: flex;
      justify-content: center;
      padding: 40px;
      background: var(--sl-color-neutral-100);
      min-height: 100vh;
      box-sizing: border-box;
      font-family: var(--sl-font-sans);
    }

    .container {
      width: 100%;
      max-width: 600px;
    }

    sl-card {
      padding: 20px;
    }

    .actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 15px;
    }
  `;

  render() {
    return html`
      <div class="container">
        <sl-card>
          <h2>Feedback</h2>

          <sl-textarea
            rows="6"
            placeholder="Type something…"
            resize="auto"
            style="margin-top: 10px;"
          ></sl-textarea>

          <div class="actions">
            <sl-button variant="primary">Submit</sl-button>
          </div>
        </sl-card>
      </div>
    `;
  }
}

customElements.define("app-sec", App);