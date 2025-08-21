import { Injectable } from '@angular/core';
import axios from 'axios';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/chat';
  private sessionId: string | null = null;

  async sendMessage(message: string): Promise<string> {
    const res = await axios.post(this.apiUrl, {
      session_id: this.sessionId,
      message: message
    });

    if (!this.sessionId) {
      this.sessionId = res.data.session_id;
    }

    return res.data.response;
  }
}
