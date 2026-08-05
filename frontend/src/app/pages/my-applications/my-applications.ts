import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { ApplicationService } from '../../services/application.service';
import { AuthService } from '../../services/auth.service';
import { ApplicationListItem } from '../../models/application.model';

@Component({
  selector: 'app-my-applications',
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule, MatToolbarModule, MatIconModule],
  templateUrl: './my-applications.html',
  styleUrl: './my-applications.scss',
})
export class MyApplications implements OnInit {
  applications = signal<ApplicationListItem[]>([]);
  loading = signal(true);

  constructor(
    private applicationService: ApplicationService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
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
