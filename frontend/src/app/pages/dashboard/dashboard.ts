import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { AuthService } from '../../services/auth.service';
import { ApplicationService } from '../../services/application.service';
import { ApplicationListItem } from '../../models/application.model';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule, MatToolbarModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  applications = signal<ApplicationListItem[]>([]);
  loading = signal(true);

  recentApplications = computed(() => this.applications().slice(0, 3));
  latestStatus = computed(() =>
    this.applications().length > 0 ? this.applications()[0].status : 'No applications yet'
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
