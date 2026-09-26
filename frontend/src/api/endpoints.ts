import { api, unwrap, unwrapEmpty } from "./client"
import type {
  Dashboard,
  LoginBody,
  Owner,
  OwnerCreate,
  OwnerUpdate,
  Payment,
  PaymentCreate,
  Pet,
  PetCreate,
  PetHistory,
  PetUpdate,
  Practice,
  PracticeUpdate,
  RegisterBody,
  RevenuePoint,
  Service,
  ServiceCreate,
  ServiceStat,
  ServiceUpdate,
  User,
  Vaccination,
  VaccinationCreate,
  Visit,
  VisitCreate,
} from "./types"

export function registerPractice(body: RegisterBody): Promise<User> {
  return unwrap(api.POST("/api/v1/auth/register", { body }))
}

export function login(body: LoginBody): Promise<{ access_token: string; token_type: string }> {
  return unwrap(api.POST("/api/v1/auth/login", { body }))
}

export function fetchMe(): Promise<User> {
  return unwrap(api.GET("/api/v1/auth/me"))
}

export function fetchPractice(): Promise<Practice> {
  return unwrap(api.GET("/api/v1/practice"))
}

export function updatePractice(body: PracticeUpdate): Promise<Practice> {
  return unwrap(api.PATCH("/api/v1/practice", { body }))
}

export function listOwners(search?: string): Promise<Owner[]> {
  return unwrap(api.GET("/api/v1/owners", { params: { query: search ? { search } : {} } }))
}

export function fetchOwner(ownerId: string): Promise<Owner> {
  return unwrap(api.GET("/api/v1/owners/{owner_id}", { params: { path: { owner_id: ownerId } } }))
}

export function createOwner(body: OwnerCreate): Promise<Owner> {
  return unwrap(api.POST("/api/v1/owners", { body }))
}

export function updateOwner(ownerId: string, body: OwnerUpdate): Promise<Owner> {
  return unwrap(
    api.PATCH("/api/v1/owners/{owner_id}", { params: { path: { owner_id: ownerId } }, body }),
  )
}

export function deleteOwner(ownerId: string): Promise<void> {
  return unwrapEmpty(api.DELETE("/api/v1/owners/{owner_id}", { params: { path: { owner_id: ownerId } } }))
}

export function listPets(search?: string, species?: string): Promise<Pet[]> {
  return unwrap(
    api.GET("/api/v1/pets", {
      params: {
        query: {
          ...(search ? { search } : {}),
          ...(species ? { species } : {}),
        },
      },
    }),
  )
}

export function fetchPet(petId: string): Promise<Pet> {
  return unwrap(api.GET("/api/v1/pets/{pet_id}", { params: { path: { pet_id: petId } } }))
}

export function createPet(body: PetCreate): Promise<Pet> {
  return unwrap(api.POST("/api/v1/pets", { body }))
}

export function updatePet(petId: string, body: PetUpdate): Promise<Pet> {
  return unwrap(api.PATCH("/api/v1/pets/{pet_id}", { params: { path: { pet_id: petId } }, body }))
}

export function deletePet(petId: string): Promise<void> {
  return unwrapEmpty(api.DELETE("/api/v1/pets/{pet_id}", { params: { path: { pet_id: petId } } }))
}

export function fetchPetHistory(petId: string): Promise<PetHistory> {
  return unwrap(api.GET("/api/v1/pets/{pet_id}/history", { params: { path: { pet_id: petId } } }))
}

export function fetchPetVisits(petId: string): Promise<Visit[]> {
  return unwrap(api.GET("/api/v1/pets/{pet_id}/visits", { params: { path: { pet_id: petId } } }))
}

export function fetchPetVaccinations(petId: string): Promise<Vaccination[]> {
  return unwrap(
    api.GET("/api/v1/pets/{pet_id}/vaccinations", { params: { path: { pet_id: petId } } }),
  )
}

export function listServices(includeInactive = false): Promise<Service[]> {
  return unwrap(
    api.GET("/api/v1/services", {
      params: { query: includeInactive ? { include_inactive: true } : {} },
    }),
  )
}

export function createService(body: ServiceCreate): Promise<Service> {
  return unwrap(api.POST("/api/v1/services", { body }))
}

export function updateService(serviceId: string, body: ServiceUpdate): Promise<Service> {
  return unwrap(
    api.PATCH("/api/v1/services/{service_id}", {
      params: { path: { service_id: serviceId } },
      body,
    }),
  )
}

export function deactivateService(serviceId: string): Promise<Service> {
  return unwrap(
    api.DELETE("/api/v1/services/{service_id}", { params: { path: { service_id: serviceId } } }),
  )
}

export function listVisits(): Promise<Visit[]> {
  return unwrap(api.GET("/api/v1/visits"))
}

export function fetchVisit(visitId: string): Promise<Visit> {
  return unwrap(api.GET("/api/v1/visits/{visit_id}", { params: { path: { visit_id: visitId } } }))
}

export function createVisit(body: VisitCreate): Promise<Visit> {
  return unwrap(api.POST("/api/v1/visits", { body }))
}

export function deleteVisit(visitId: string): Promise<void> {
  return unwrapEmpty(
    api.DELETE("/api/v1/visits/{visit_id}", { params: { path: { visit_id: visitId } } }),
  )
}

export function createPayment(body: PaymentCreate): Promise<Payment> {
  return unwrap(api.POST("/api/v1/payments", { body }))
}

export function listVaccinations(): Promise<Vaccination[]> {
  return unwrap(api.GET("/api/v1/vaccinations"))
}

export function listUpcomingVaccinations(days: number): Promise<Vaccination[]> {
  return unwrap(api.GET("/api/v1/vaccinations/upcoming", { params: { query: { days } } }))
}

export function createVaccination(body: VaccinationCreate): Promise<Vaccination> {
  return unwrap(api.POST("/api/v1/vaccinations", { body }))
}

export function deleteVaccination(vaccinationId: string): Promise<void> {
  return unwrapEmpty(
    api.DELETE("/api/v1/vaccinations/{vaccination_id}", {
      params: { path: { vaccination_id: vaccinationId } },
    }),
  )
}

export function fetchDashboard(): Promise<Dashboard> {
  return unwrap(api.GET("/api/v1/analytics/dashboard"))
}

export function fetchRevenue(from?: string, to?: string): Promise<RevenuePoint[]> {
  return unwrap(
    api.GET("/api/v1/analytics/revenue", {
      params: {
        query: {
          ...(from ? { from } : {}),
          ...(to ? { to } : {}),
        },
      },
    }),
  )
}

export function fetchServiceStats(from?: string, to?: string): Promise<ServiceStat[]> {
  return unwrap(
    api.GET("/api/v1/analytics/services", {
      params: {
        query: {
          ...(from ? { from } : {}),
          ...(to ? { to } : {}),
        },
      },
    }),
  )
}
