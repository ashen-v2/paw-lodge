import type { components } from "./generated/schema"

export type Schema<Name extends keyof components["schemas"]> = components["schemas"][Name]

export type User = Schema<"UserRead">
export type Practice = Schema<"PracticeRead">
export type PracticeUpdate = Schema<"PracticeUpdate">
export type Owner = Schema<"OwnerRead">
export type OwnerCreate = Schema<"OwnerCreate">
export type OwnerUpdate = Schema<"OwnerUpdate">
export type Pet = Schema<"PetRead">
export type PetCreate = Schema<"PetCreate">
export type PetUpdate = Schema<"PetUpdate">
export type PetHistory = Schema<"PetHistory">
export type TimelineEvent = Schema<"TimelineEvent">
export type Service = Schema<"ServiceRead">
export type ServiceCreate = Schema<"ServiceCreate">
export type ServiceUpdate = Schema<"ServiceUpdate">
export type Visit = Schema<"VisitRead">
export type VisitCreate = Schema<"VisitCreate">
export type VisitItemCreate = Schema<"VisitItemCreate">
export type Payment = Schema<"PaymentRead">
export type PaymentCreate = Schema<"PaymentCreate">
export type Vaccination = Schema<"VaccinationRead">
export type VaccinationCreate = Schema<"VaccinationCreate">
export type Dashboard = Schema<"DashboardRead">
export type RevenuePoint = Schema<"RevenuePoint">
export type ServiceStat = Schema<"ServiceStat">
export type RegisterBody = Schema<"RegisterRequest">
export type LoginBody = Schema<"LoginRequest">
