import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Application, ApplicationCreateRequest, ApplicationListItem } from '../models/application.model';

@Injectable({ providedIn: 'root' })
export class ApplicationService {
  constructor(private http: HttpClient) {}

  create(data: ApplicationCreateRequest): Observable<Application> {
    return this.http.post<Application>(`${environment.applicationApiUrl}/applications`, data);
  }

  getMyApplications(): Observable<ApplicationListItem[]> {
    return this.http.get<ApplicationListItem[]>(`${environment.applicationApiUrl}/applications`);
  }

  getById(id: string): Observable<Application> {
    return this.http.get<Application>(`${environment.applicationApiUrl}/applications/${id}`);
  }
}
