import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../services/auth.service';
import { ApplicationService } from '../../services/application.service';
import { ApplicationListItem } from '../../models/application.model';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule, MatToolbarModule, MatIconModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class DashboardComponent implements OnInit {
  applications = signal<ApplicationListItem[]>([]);
  loading = signal(true);

  recentApplications = computed(() => this.applications().slice(0, 5));

  totalCount = computed(() => this.applications().length);
  approvedCount = computed(() => this.applications().filter(a => a.status === 'APPROVED').length);
  rejectedCount = computed(() => this.applications().filter(a => a.status === 'REJECTED').length);
  pendingCount = computed(() =>
    this.applications().filter(a => a.status === 'SUBMITTED' || a.status === 'UNDER_REVIEW').length
  );

  constructor(
    public authService: AuthService,
    private applicationService: ApplicationService
  ) {}

  ngOnInit(): void {
    this.authService.fetchCurrentUser().subscribe();

    this.applicationService.getMyApplications().subscribe({
      next: (apps) => {
        this.applications.set(apps);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  logout(): void {
    this.authService.logout();
  }
}
