import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { ApplicationService } from '../../services/application.service';
import { AuthService } from '../../services/auth.service';
import { Application } from '../../models/application.model';

@Component({
  selector: 'app-application-detail',
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule, MatToolbarModule],
  templateUrl: './application-detail.html',
  styleUrl: './application-detail.scss',
})
export class ApplicationDetail implements OnInit {
  application = signal<Application | null>(null);
  loading = signal(true);
  errorMessage = signal('');

  constructor(
    private route: ActivatedRoute,
    private applicationService: ApplicationService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) return;

    this.applicationService.getById(id).subscribe({
      next: (app) => {
        this.application.set(app);
        this.loading.set(false);
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Failed to load application.');
      },
    });
  }

  logout(): void {
    this.authService.logout();
  }
}
