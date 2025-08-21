import { Component } from '@angular/core';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-root',
  template: `
    <div class="chat-container">
      <h2>Simple Q&A Chatbot</h2>

      <div class="chat-box">
        <div *ngFor="let msg of messages" [ngClass]="msg.role">
          <b *ngIf="msg.role === 'user'">Q:</b>
          <b *ngIf="msg.role === 'bot'">A:</b>
          {{msg.text}}
        </div>
      </div>

      <div class="input-box">
        <input [(ngModel)]="input" (keyup.enter)="send()" placeholder="Type your question"/>
        <button (click)="send()">Ask</button>
      </div>
    </div>
  `,
  styles: [`
    .chat-container { max-width: 500px; margin: auto; padding: 20px; font-family: Arial; }
    .chat-box { background: #f4f4f4; padding: 15px; border-radius: 8px; min-height: 200px; }
    .user { text-align: right; color: blue; margin: 5px 0; }
    .bot { text-align: left; color: green; margin: 5px 0; }
    .input-box { margin-top: 10px; }
    input { width: 75%; padding: 8px; }
    button { padding: 8px 12px; margin-left: 5px; }
  `]
})
export class AppComponent {
  input = '';
  messages: {role: 'user' | 'bot', text: string}[] = [];

  constructor(private chatService: ChatService) {}

  async send() {
    if (!this.input.trim()) return;

    // Add user Q
    this.messages.push({role: 'user', text: this.input});

    // Call backend
    const reply = await this.chatService.sendMessage(this.input);

    // Add bot A
    this.messages.push({role: 'bot', text: reply});

    this.input = '';
  }
}
