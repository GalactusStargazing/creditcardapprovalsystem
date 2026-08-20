import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'register', loadComponent: () => import('./pages/register/register').then(m => m.RegisterComponent) },
  { path: 'login', loadComponent: () => import('./pages/login/login').then(m => m.LoginComponent) },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard').then(m => m.DashboardComponent),
    canActivate: [authGuard],
  },
  {
    path: 'apply',
    loadComponent: () => import('./pages/apply/apply').then(m => m.ApplyComponent),
    canActivate: [authGuard],
  },
  {
    path: 'applications',
    loadComponent: () => import('./pages/my-applications/my-applications').then(m => m.MyApplicationsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'applications/:id',
    loadComponent: () => import('./pages/application-detail/application-detail').then(m => m.ApplicationDetailComponent),
    canActivate: [authGuard],
  },
  { path: '**', redirectTo: 'login' },
];
