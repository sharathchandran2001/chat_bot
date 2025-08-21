import { Component } from '@angular/core';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-root',
  template: `
    <div class="chat-wrapper">
      <div class="chat-header">
        🤖 MiniBot
      </div>

      <div class="chat-box" #chatBox>
        <div *ngFor="let msg of messages" class="chat-message" [ngClass]="msg.role">
          <div class="bubble">
            <span *ngIf="msg.role === 'user'">🙋‍♂️</span>
            <span *ngIf="msg.role === 'bot'">🤖</span>
            {{ msg.text }}
          </div>
        </div>
      </div>

      <div class="chat-input">
        <input [(ngModel)]="input" (keyup.enter)="send()" placeholder="Type your message..." />
        <button (click)="send()">Send</button>
      </div>
    </div>
  `,
  styles: [`
    .chat-wrapper {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      width: 400px;
      height: 600px;
      margin: 40px auto;
      border-radius: 16px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.15);
      overflow: hidden;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #ffffff;
    }

    .chat-header {
      background: linear-gradient(90deg, #4e54c8, #8f94fb);
      color: white;
      padding: 15px;
      font-size: 18px;
      font-weight: bold;
      text-align: center;
    }

    .chat-box {
      flex: 1;
      padding: 15px;
      overflow-y: auto;
      background: #f9f9fb;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .chat-message {
      display: flex;
      align-items: flex-start;
    }

    .chat-message.user {
      justify-content: flex-end;
    }

    .chat-message.bot {
      justify-content: flex-start;
    }

    .bubble {
      max-width: 70%;
      padding: 10px 14px;
      border-radius: 16px;
      font-size: 15px;
      line-height: 1.4;
      display: inline-block;
      word-wrap: break-word;
    }

    .chat-message.user .bubble {
      background: #4e54c8;
      color: white;
      border-bottom-right-radius: 4px;
    }

    .chat-message.bot .bubble {
      background: #e6e6e6;
      color: #333;
      border-bottom-left-radius: 4px;
    }

    .chat-input {
      display: flex;
      border-top: 1px solid #ddd;
      padding: 10px;
      background: white;
    }

    .chat-input input {
      flex: 1;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 20px;
      outline: none;
      font-size: 14px;
    }

    .chat-input button {
      margin-left: 10px;
      padding: 10px 16px;
      border: none;
      border-radius: 20px;
      background: #4e54c8;
      color: white;
      cursor: pointer;
      transition: background 0.3s ease;
    }

    .chat-input button:hover {
      background: #3c3fa3;
    }
  `]
})
export class AppComponent {
  input = '';
  messages: { role: 'user' | 'bot', text: string }[] = [];

  constructor(private chatService: ChatService) {}

  async send() {
    if (!this.input.trim()) return;

    this.messages.push({ role: 'user', text: this.input });

    const reply = await this.chatService.sendMessage(this.input);
    this.messages.push({ role: 'bot', text: reply });

    this.input = '';
    setTimeout(() => {
      const chatBox = document.querySelector('.chat-box');
      if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    }, 100);
  }
}
