import datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from typing import Union

# ESG Question Models
class ESGQuestion(BaseModel):
    question_id: str  # e.g., "A0/1", "C1_1"
    response: Any  # Flexible to handle text, tables, nested objects

class ESGQuestionUpdate(BaseModel):
    response: Any

# User Models
class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Make id optional
    password: str
    email: Optional[EmailStr] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        allow_population_by_field_name = True  # Allow alias "_id"

class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None

# Helper class for PyObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, values=None):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.str_schema(),
        ], custom_error_type='invalid_objectid', custom_error_message='Invalid ObjectId')
        
# Question mapping
class QuestionMapping(BaseModel):
    question_id: str
    schema_path: str
    section: str
    question_name: str

# Manager details
class PlantManager(BaseModel):
    name: str
    employee_id: str
    contact_email: str
    contact_phone: str

# Location coordinates
class Coordinates(BaseModel):
    latitude: float
    longitude: float

# Plant location
class Location(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    

# Products/Services
class ProductService(BaseModel):
    product_service: str
    nic_code: str
    percentage_turnover: float

# Gender breakdown
class GenderBreakdown(BaseModel):
    number: int
    percentage: float

# Employee/Worker category
class EmployeeCategory(BaseModel):
    total: int
    male: GenderBreakdown
    female: GenderBreakdown

# Turnover rate per FY
class TurnoverRateFY(BaseModel):
    male: float
    female: float
    total: float

# Turnover rate
class TurnoverRate(BaseModel):
    current_fy: Optional[TurnoverRateFY] = None
    previous_fy: Optional[TurnoverRateFY] = None
    two_years_ago: Optional[TurnoverRateFY] = None

# General Disclosures
class GeneralDisclosures(BaseModel):
    facility_type: Optional[str] = None
    owned_or_leased: Optional[str] = None
    products_services: Optional[List[ProductService]] = None
    employees: Optional[Dict[str, EmployeeCategory]] = None
    workers: Optional[Dict[str, EmployeeCategory]] = None
    differently_abled_employees: Optional[Dict[str, EmployeeCategory]] = None
    differently_abled_workers: Optional[Dict[str, EmployeeCategory]] = None
    turnover_rate: Optional[TurnoverRate] = None

# Policy details
class Policy(BaseModel):
    exists: bool
    board_approved: Optional[bool] = None  # Made optional
    web_link: str

# Sustainability commitment
class SustainabilityCommitment(BaseModel):
    target: str
    timeline: str

# Performance against target
class PerformanceAgainstTarget(BaseModel):
    achieved: bool
    reason: str

# Sustainability oversight
class SustainabilityOversightDetails(BaseModel):
    name: str
    chairperson: str
    meetings_per_year: int

class SustainabilityOversight(BaseModel):
    committee_exists: Optional[bool] = None
    details: Optional[SustainabilityOversightDetails] = None

# Management and Process Disclosures
class ManagementAndProcess(BaseModel):
    policies: Optional[Dict[str, Policy]] = None
    policies_translated_to_procedures: Optional[bool] = None
    policies_extend_to_value_chain: Optional[bool] = None
    certifications: Optional[List[str]] = None
    sustainability_commitments: Optional[Dict[str, SustainabilityCommitment]] = None
    performance_against_targets: Optional[Dict[str, PerformanceAgainstTarget]] = None
    sustainability_oversight: Optional[SustainabilityOversight] = None

# Training coverage
class TrainingCoverage(BaseModel):
    total_programs: int
    topics: List[str]
    coverage_percentage: float

# Fine or penalty
class FinePenalty(BaseModel):
    principle: str
    regulatory_body: str
    amount_inr: int
    brief: str
    appeal_preferred: bool

# Disciplinary actions
class DisciplinaryActions(BaseModel):
    employees: int
    workers: int

# Complaints
class Complaints(BaseModel):
    number: int
    remarks: str

# Principle 1: Ethics and Transparency
class Principle1(BaseModel):
    training_coverage: Optional[Dict[str, TrainingCoverage]] = None
    fines_penalties: Optional[List[FinePenalty]] = None
    anti_corruption_policy: Optional[Policy] = None
    disciplinary_actions_bribery: Optional[Dict[str, DisciplinaryActions]] = None
    conflict_of_interest_complaints: Optional[Dict[str, Complaints]] = None

# R&D and Capex investments
class RDCapex(BaseModel):
    rd_percentage: float
    capex_percentage: float
    details: str

# Waste reclamation
class WasteReclamation(BaseModel):
    plastics: Optional[str] = None
    e_waste: Optional[str] = None
    hazardous_waste: Optional[str] = None
    other_waste: Optional[str] = None

# EPR status
class EPRStatus(BaseModel):
    status: str
    in_line_with_plan: bool

# Sustainable sourcing
class SustainableSourcing(BaseModel):
    percentage_sourced_sustainably: float
    measures_taken: List[str]

# Principle 2: Sustainable Products
class Principle2(BaseModel):
    rd_capex_investments: Optional[Dict[str, RDCapex]] = None
    sustainable_sourcing: Optional[SustainableSourcing] = None
    waste_reclamation_processes: Optional[WasteReclamation] = None
    epr_applicable: Optional[EPRStatus] = None

# Well-being benefits
class WellbeingBenefits(BaseModel):
    male: Optional[Dict[str, Union[int, float]]] = None
    female: Optional[Dict[str, Union[int, float]]] = None

# Employee well-being
class EmployeeWellbeing(BaseModel):
    permanent_employees: Optional[Dict[str, WellbeingBenefits]] = None
    permanent_workers: Optional[Dict[str, WellbeingBenefits]] = None

# Retirement benefits
class RetirementBenefit(BaseModel):
    employees_percentage: float
    workers_percentage: float
    deposited: str

# Retirement benefits per FY
class RetirementBenefitsFY(BaseModel):
    pf: Optional[RetirementBenefit] = None
    gratuity: Optional[RetirementBenefit] = None
    esi: Optional[RetirementBenefit] = None

# Grievance mechanism
class GrievanceMechanism(BaseModel):
    exists: bool
    details: str

# Safety incidents
class SafetyIncidents(BaseModel):
    ltifr: Optional[Dict[str, float]] = None
    total_injuries: Optional[Dict[str, int]] = None
    fatalities: Optional[Dict[str, int]] = None
    high_consequence_injuries: Optional[Dict[str, int]] = None

# Health and safety complaints
class HealthSafetyComplaints(BaseModel):
    filed: int
    pending: int
    remarks: str

# Accessibility measures
class AccessibilityMeasures(BaseModel):
    measures: List[str]

# Principle 3: Employee Well-being
class Principle3(BaseModel):
    employee_wellbeing: Optional[EmployeeWellbeing] = None
    retirement_benefits: Optional[Dict[str, RetirementBenefitsFY]] = None
    accessibility: Optional[AccessibilityMeasures] = None
    equal_opportunity_policy: Optional[Policy] = None
    grievance_mechanisms: Optional[Dict[str, GrievanceMechanism]] = None
    safety_incidents: Optional[Dict[str, SafetyIncidents]] = None
    health_safety_complaints: Optional[Dict[str, Dict[str, HealthSafetyComplaints]]] = None

# Stakeholder engagement
class StakeholderEngagement(BaseModel):
    group: str
    vulnerable_marginalized: bool
    channels: List[str]
    frequency: str
    purpose: str

# Material issues identified
class MaterialIssues(BaseModel):
    issues: List[str]

# Principle 4: Stakeholder Engagement
class Principle4(BaseModel):
    stakeholder_engagement: Optional[List[StakeholderEngagement]] = None
    material_issues_identified: Optional[MaterialIssues] = None

# Human rights training
class HumanRightsTraining(BaseModel):
    total: int
    covered: int
    percentage: float

# Minimum wages
class MinimumWages(BaseModel):
    total: int
    equal_to_minimum: int
    above_minimum: int

# Human rights grievances
class HumanRightsGrievance(BaseModel):
    filed: int
    pending: int
    remarks: str

# Human rights complaints
class HumanRightsComplaints(BaseModel):
    current_fy: HumanRightsGrievance
    previous_fy: HumanRightsGrievance

# Principle 5: Human Rights
class Principle5(BaseModel):
    human_rights_training: Optional[Dict[str, Dict[str, HumanRightsTraining]]] = None
    minimum_wages: Optional[Dict[str, Dict[str, MinimumWages]]] = None
    human_rights_grievances: Optional[HumanRightsComplaints] = None
    human_rights_policy: Optional[Policy] = None

# Energy consumption
class EnergyConsumption(BaseModel):
    total_electricity_gj: Optional[float] = None
    total_fuel_gj: Optional[float] = None
    other_sources_gj: Optional[float] = None
    total_energy_gj: Optional[float] = None
    intensity_per_inr: Optional[float] = None

# External assessment
class ExternalAssessment(BaseModel):
    conducted: bool
    agency: str

# Water withdrawal
class WaterWithdrawal(BaseModel):
    surface_water_kl: Optional[float] = None
    groundwater_kl: Optional[float] = None
    third_party_water_kl: Optional[float] = None
    total_withdrawal_kl: Optional[float] = None

# Water discharge
class WaterDischargeType(BaseModel):
    no_treatment_kl: Optional[float] = None
    treated_kl: Optional[float] = None
    treatment_level: Optional[str] = None

# Water discharge
class WaterDischarge(BaseModel):
    surface_water: Optional[WaterDischargeType] = None
    groundwater: Optional[WaterDischargeType] = None
    third_party: Optional[WaterDischargeType] = None
    total_discharge_kl: Optional[float] = None

# Water management
class WaterManagement(BaseModel):
    withdrawal: Optional[WaterWithdrawal] = None
    consumption_kl: Optional[float] = None
    intensity_per_inr: Optional[float] = None
    discharge: Optional[WaterDischarge] = None

# GHG emissions
class GHGEmissions(BaseModel):
    scope_1_tons_co2e: Optional[float] = None
    scope_2_tons_co2e: Optional[float] = None
    intensity_per_inr: Optional[float] = None

# Waste metrics
class WasteMetrics(BaseModel):
    plastic_waste_tons: Optional[float] = None
    e_waste_tons: Optional[float] = None
    hazardous_waste_tons: Optional[float] = None
    other_non_hazardous_tons: Optional[float] = None
    total_tons: Optional[float] = None

# Waste recovered
class WasteRecovered(BaseModel):
    recycled_tons: Optional[float] = None
    reused_tons: Optional[float] = None
    other_recovery_tons: Optional[float] = None
    total_recovered_tons: Optional[float] = None

# Waste disposed
class WasteDisposed(BaseModel):
    incineration_tons: Optional[float] = None
    landfilling_tons: Optional[float] = None
    other_disposal_tons: Optional[float] = None
    total_disposed_tons: Optional[float] = None

# Waste management
class WasteManagement(BaseModel):
    generated: Optional[WasteMetrics] = None
    recovered: Optional[WasteRecovered] = None
    disposed: Optional[WasteDisposed] = None

# Zero liquid discharge
class ZeroLiquidDischarge(BaseModel):
    implemented: bool
    details: str

# Environmental compliance
class EnvironmentalCompliance(BaseModel):
    non_compliances: int
    details: str

# Principle 6: Environment
class Principle6(BaseModel):
    energy_consumption: Optional[Dict[str, Union[EnergyConsumption, ExternalAssessment]]] = None
    water_management: Optional[Dict[str, Union[WaterManagement, ExternalAssessment]]] = None
    ghg_emissions: Optional[Dict[str, Union[GHGEmissions, ExternalAssessment]]] = None
    waste_management: Optional[Dict[str, Union[WasteManagement, ExternalAssessment]]] = None
    zero_liquid_discharge: Optional[ZeroLiquidDischarge] = None
    environmental_compliance: Optional[EnvironmentalCompliance] = None

# Trade association
class TradeAssociation(BaseModel):
    name: str
    reach: str

# Anti-competitive conduct
class AntiCompetitiveConduct(BaseModel):
    instances: int

# Principle 7: Public Policy
class Principle7(BaseModel):
    trade_associations: Optional[List[TradeAssociation]] = None
    anti_competitive_conduct: Optional[Dict[str, AntiCompetitiveConduct]] = None

# Social impact assessment
class SocialImpactAssessment(BaseModel):
    project_name: str
    notification_no: str
    date: datetime
    external_agency: bool
    public_domain: bool
    web_link: str

# Community grievance mechanism
class CommunityGrievanceMechanism(BaseModel):
    exists: bool
    details: str

# CSR project
class CSRProject(BaseModel):
    name: str
    investment_inr: float
    beneficiaries: int

# Principle 8: Inclusive Growth
class Principle8(BaseModel):
    social_impact_assessments: Optional[List[SocialImpactAssessment]] = None
    community_grievance_mechanisms: Optional[CommunityGrievanceMechanism] = None
    csr_projects: Optional[List[CSRProject]] = None

# Consumer complaints
class ConsumerComplaint(BaseModel):
    received: int
    pending: int
    remarks: str

# Cyber security measures
class CyberSecurityMeasures(BaseModel):
    measures: List[str]

# Principle 9: Consumer Responsibility
class Principle9(BaseModel):
    consumer_complaints: Optional[Dict[str, Dict[str, ConsumerComplaint]]] = None
    cyber_security_policy: Optional[Policy] = None
    cyber_security_measures: Optional[CyberSecurityMeasures] = None

# Principle-wise Performance
class PrincipleWisePerformance(BaseModel):
    principle_1: Optional[Principle1] = None
    principle_2: Optional[Principle2] = None
    principle_3: Optional[Principle3] = None
    principle_4: Optional[Principle4] = None
    principle_5: Optional[Principle5] = None
    principle_6: Optional[Principle6] = None
    principle_7: Optional[Principle7] = None
    principle_8: Optional[Principle8] = None
    principle_9: Optional[Principle9] = None

# Update log
class UpdateLog(BaseModel):
    question_id: str
    updated_by: str
    updated_at: datetime
    schema_path: str

# Main Plant model
class Plant(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    plant_id: str
    plant_name: str
    company_id: PyObjectId
    plant_manager: Optional[PlantManager] = None
    location: Optional[Location] = None
    operational_status: Optional[str] = None
    establishment_date: Optional[datetime] = None
    production_capacity: Optional[int] = None
    reporting_year: Optional[int] = None
    general_disclosures: Optional[GeneralDisclosures] = None
    management_and_process: Optional[ManagementAndProcess] = None
    principle_wise_performance: Optional[PrincipleWisePerformance] = None
    data_ownership: Optional[Dict[str, List[str]]] = None
    updates: Optional[List[UpdateLog]] = None
    question_mappings: Optional[List[QuestionMapping]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

# Company Model
class ContactPerson(BaseModel):
    name: str
    telephone: str
    email: EmailStr

class HoldingSubsidiaryAssociate(BaseModel):
    name: str
    type: str  # e.g., "Subsidiary", "Holding", "Associate"
    percentageSharesHeld: float
    participatesInBRSR: bool

class CSRDetails(BaseModel):
    applicable: bool
    turnover_inr: float
    net_worth_inr: float

class ComplaintsGrievances(BaseModel):
    current_fy: Dict[str, Union[int, str]]  # filed, pending, remarks
    previous_fy: Dict[str, Union[int, str]]

class TransparencyCompliances(BaseModel):
    complaints_grievances: ComplaintsGrievances
    compliance_with_disclosures: bool

class GeneralDisclosuresCompany(BaseModel):  # Renamed to avoid conflict
    csr_details: CSRDetails
    transparency_compliances: TransparencyCompliances

class PolicyCompany(BaseModel):  # Renamed to avoid conflict
    exists: bool
    board_approved: Optional[bool] = None  # Made optional
    web_link: HttpUrl

class SustainabilityCommitmentCompany(BaseModel):  # Renamed to avoid conflict
    target: str
    timeline: str

class PerformanceAgainstTargetCompany(BaseModel):  # Renamed to avoid conflict
    achieved: bool
    reason: str

class SustainabilityOversightCompany(BaseModel):  # Renamed to avoid conflict
    committee_exists: bool
    details: Dict[str, Union[str, int]]  # name, chairperson, meetings_per_year

class ManagementAndProcessCompany(BaseModel):  # Renamed to avoid conflict
    policies: Dict[str, PolicyCompany]  # principle_1 to principle_9
    policies_translated_to_procedures: bool
    policies_extend_to_value_chain: bool
    certifications: List[str]
    sustainability_commitments: Dict[str, SustainabilityCommitmentCompany]
    performance_against_targets: Dict[str, PerformanceAgainstTargetCompany]
    sustainability_oversight: SustainabilityOversightCompany

class AntiCorruptionPolicy(BaseModel):
    exists: bool
    web_link: HttpUrl

class Principle1Company(BaseModel):  # Renamed to avoid conflict
    anti_corruption_policy: AntiCorruptionPolicy

class Principle7Company(BaseModel):  # Renamed to avoid conflict
    trade_association_memberships: List[Dict[str, Union[str, List[str]]]]

class PrincipleWisePerformanceCompany(BaseModel):  # Renamed to avoid conflict
    principle_1: Principle1Company
    principle_2: Dict[str, Any] = {}
    principle_3: Dict[str, Any] = {}
    principle_4: Dict[str, Any] = {}
    principle_5: Dict[str, Any] = {}
    principle_6: Dict[str, Any] = {}
    principle_7: Principle7Company
    principle_8: Dict[str, Any] = {}
    principle_9: Dict[str, Any] = {}

class UpdateLogCompany(BaseModel):  # Renamed to avoid conflict
    question_id: str
    updated_by: str
    updated_at: datetime
    schema_path: str

class Company(BaseModel):
    company_id: str
    name: str
    corporateIdentityNumber: str
    yearOfIncorporation: int
    registeredOfficeAddress: str
    corporateAddress: str
    email: EmailStr
    telephone: str
    website: HttpUrl
    financialYear: str
    stockExchanges: List[str]
    paidUpCapital: float
    contactPerson: ContactPerson
    reportingBoundary: str
    holdingSubsidiaryAssociateCompanies: List[HoldingSubsidiaryAssociate]
    plants: List[str]  # List of plant_id references
    general_disclosures: GeneralDisclosuresCompany
    management_and_process: ManagementAndProcessCompany
    principle_wise_performance: PrincipleWisePerformanceCompany
    data_ownership: Dict[str, List[str]]
    updates: List[UpdateLogCompany]
    created_at: datetime
    updated_at: Optional[datetime] = None
    _id: Optional[ObjectId] = None  # MongoDB ObjectId
