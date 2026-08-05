import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { ApplicationService } from '../../services/application.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-apply',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatCardModule,
    MatToolbarModule,
  ],
  templateUrl: './apply.html',
  styleUrl: './apply.scss',
})
export class Apply {
  errorMessage = signal('');
  loading = signal(false);

  cardOptions = [
    { value: 'SILVER', label: 'Silver', fee: '₹500/year', limit: 'Up to ₹1,00,000' },
    { value: 'GOLD', label: 'Gold', fee: '₹1,500/year', limit: 'Up to ₹3,00,000' },
    { value: 'PLATINUM', label: 'Platinum', fee: '₹3,000/year', limit: 'Up to ₹10,00,000' },
  ];

  form: ReturnType<FormBuilder['group']>;

  constructor(
    private fb: FormBuilder,
    private applicationService: ApplicationService,
    private authService: AuthService,
    private router: Router
  ) {
    this.form = this.fb.group({
      full_name: ['', Validators.required],
      date_of_birth: ['', Validators.required],
      pan_number: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(10)]],
      mobile_number: ['', [Validators.required, Validators.minLength(10)]],
      email: ['', [Validators.required, Validators.email]],
      address: ['', Validators.required],
      occupation: ['SALARIED', Validators.required],
      employer: [''],
      monthly_income: [null, [Validators.required, Validators.min(1)]],
      existing_loan_amount: [0, [Validators.required, Validators.min(0)]],
      credit_score: [null, [Validators.required, Validators.min(300), Validators.max(900)]],
      card_type: ['GOLD', Validators.required],
    });
  }

  onSubmit(): void {
    this.errorMessage.set('');

    if (this.form.invalid) {
      this.errorMessage.set('Please fill in all required fields correctly.');
      return;
    }

    this.loading.set(true);
    this.applicationService.create(this.form.value as any).subscribe({
      next: (application) => {
        this.loading.set(false);
        this.router.navigate(['/applications', application.id]);
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Failed to submit application. Please try again.');
      },
    });
  }

  logout(): void {
    this.authService.logout();
  }
}
