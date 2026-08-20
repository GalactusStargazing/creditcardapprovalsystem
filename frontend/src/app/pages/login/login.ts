import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class LoginComponent {
  errorMessage = signal('');
  loading = signal(false);
  form: ReturnType<FormBuilder['group']>;

  cardTiers = [
    { name: 'Platinum', fee: '₹3,000/year', limit: 'Up to ₹10,00,000' },
    { name: 'Gold', fee: '₹1,500/year', limit: 'Up to ₹3,00,000' },
    { name: 'Silver', fee: '₹500/year', limit: 'Up to ₹1,00,000' },
  ];

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.form = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
    });
  }

  onSubmit(): void {
    this.errorMessage.set('');

    if (this.form.invalid) {
      return;
    }

    const { email, password } = this.form.value;

    this.loading.set(true);
    this.authService.login({ email: email!, password: password! }).subscribe({
      next: () => {
        this.loading.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Login failed. Please try again.');
      },
    });
  }
}
