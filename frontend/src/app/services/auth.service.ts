import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoginRequest, RegisterRequest, TokenResponse, User } from '../models/user.model';

const TOKEN_KEY = 'access_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  currentUser = signal<User | null>(null);

  constructor(private http: HttpClient, private router: Router) {}

  register(data: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${environment.authApiUrl}/auth/register`, data);
  }

  login(data: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.authApiUrl}/auth/login`, data).pipe(
      tap((res) => {
        localStorage.setItem(TOKEN_KEY, res.access_token);
      })
    );
  }

  fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(`${environment.authApiUrl}/auth/me`).pipe(
      tap((user) => this.currentUser.set(user))
    );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}
