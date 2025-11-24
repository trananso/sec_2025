import { LitElement, html, css } from "lit";
import "@shoelace-style/shoelace/dist/components/textarea/textarea.js";
import "@shoelace-style/shoelace/dist/components/button/button.js";
import "@shoelace-style/shoelace/dist/components/card/card.js";

import "./JobBoardPage.js"

export default class App extends LitElement {
  static styles = css`
  `;

  render() {    
    return html`
    <sl-theme name="dark">
        <job-board-page></job-board-page>
    </sl-theme>
    `;  
  }
}

customElements.define("app-sec", App);