export type CardType = 'SILVER' | 'GOLD' | 'PLATINUM';
export type ApplicationStatus = 'SUBMITTED' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED';

export interface ApplicationCreateRequest {
  full_name: string;
  date_of_birth: string;
  pan_number: string;
  mobile_number: string;
  email: string;
  address: string;
  occupation: string;
  employer?: string;
  monthly_income: number;
  existing_loan_amount: number;
  credit_score: number;
  card_type: CardType;
}

export interface Application {
  id: string;
  full_name: string;
  date_of_birth: string;
  pan_number: string;
  mobile_number: string;
  email: string;
  address: string;
  occupation: string;
  employer: string | null;
  monthly_income: number;
  existing_loan_amount: number;
  credit_score: number;
  card_type: CardType;
  status: ApplicationStatus;
  card_number: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationListItem {
  id: string;
  card_type: CardType;
  status: ApplicationStatus;
  created_at: string;
}
