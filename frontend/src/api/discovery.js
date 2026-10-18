import { apiRequest } from './client'
function buildQuery(values) {
  const params = new URLSearchParams()
  Object.entries(values).forEach(([key,value]) => { if (value !== undefined && value !== null && String(value).trim()) params.set(key,String(value).trim()) })
  return params.toString()
}
export async function getElderCareDirectory({search='',location='',facility=''}={}) {
  const query=buildQuery({search,location,facility})
  return apiRequest(query?'/organizations/elder-care?'+query:'/organizations/elder-care',{authenticated:false})
}
export async function getCaregiverDirectory({search='',location='',serviceType=''}={}) {
  const query=buildQuery({search,location,service_type:serviceType})
  return apiRequest(query?'/caregivers?'+query:'/caregivers',{authenticated:false})
}
export async function getDonationCampaigns() { return apiRequest('/donation-campaigns',{authenticated:false}) }
export async function getDonationNeeds() { return apiRequest('/donation-needs',{authenticated:false}) }
export async function getPublicImpactUpdates() { return apiRequest('/impact-updates',{authenticated:false}) }
export async function getPublicOrphanageProfile(organizationId) {
  return apiRequest('/orphanages/'+encodeURIComponent(organizationId)+'/public-profile',{authenticated:false})
}
export async function createInKindPledge(needId,{quantity,notes=''}={}) {
  return apiRequest('/donation-needs/'+encodeURIComponent(needId)+'/in-kind-pledges',{method:'POST',body:JSON.stringify({quantity:Number(quantity),notes:notes.trim()||null})})
}
