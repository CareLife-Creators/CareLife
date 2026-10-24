"""Create a small, fictional CareLife walkthrough using the real API workflows.

Run from backend with:
    .venv/Scripts/python scripts/create_demo_scenario.py

The script creates fresh suffixed accounts, requests staff roles through the
admin queue, registers and approves organizations, and submits sample records.
It never writes directly to application tables. All records are labelled DEMO.
"""

from datetime import date, timedelta
from getpass import getpass
import json
import secrets
import sys
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8000"
DEMO_PASSWORD = "CareLifeDemo2026!"


def request(method, path, body=None, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"{method} {path} returned {exc.code}: {detail}") from exc


def login(email, password):
    result = request("POST", "/auth/login", {"email": email, "password": password})
    return {"token": result["access_token"], "user_id": result["user_id"]}


def signup(suffix, name, role, index):
    email = f"demo.{suffix}.{name}@example.com"
    request("POST", "/auth/signup", {
        "email": email,
        "password": DEMO_PASSWORD,
        "full_name": "DEMO " + name.replace(".", " ").title(),
        "phone": f"+880170000{index:04d}",
        "role": role,
    })
    return {"email": email, **login(email, DEMO_PASSWORD)}


def make_staff(suffix, admin_token, role, name, index):
    account = signup(suffix, name, "parent_guardian", index)
    if request("GET", "/users/me/profile", token=account["token"])["role"] != role:
        ticket = request("POST", "/users/me/role-requests", {
            "requested_role": role,
            "note": "DEMO test scenario — fictional organization and sample workflow.",
        }, account["token"])
        request("POST", f"/admin/role-requests/{ticket['id']}/approve", token=admin_token)
        account.update(login(account["email"], DEMO_PASSWORD))
    return account


def register_org(account, admin_token, name, kind, city, lat, lon, index):
    account_rows = request("GET", "/admin/users", token=admin_token)
    admin_account = next(row for row in account_rows if row["user_id"] == account["user_id"])
    owned_ids = set(admin_account.get("organization_ids", []))
    existing = next((item for item in request("GET", "/organizations/verification/tracking", token=admin_token)
                     if item["organization_name"] == "[DEMO] " + name
                     and item["organization_id"] in owned_ids), None)
    if existing:
        org_id = existing["organization_id"]
        if existing["status"] != "verified":
            request("POST", f"/organizations/{org_id}/verification/approve", token=admin_token)
    else:
        org = request("POST", "/organizations/register", {
            "organization_name": "[DEMO] " + name,
            "organization_type": kind,
            "description": "Fictional test organization. Sample information for trying the CareLife workflow; not a real provider.",
            "location": city + ", Bangladesh",
            "latitude": lat,
            "longitude": lon,
            "contact": "+880 1700 000 000",
            "license_number": f"DEMO-{kind.upper()}-{index:03d}",
            "license_expiry_date": (date.today() + timedelta(days=365)).isoformat(),
        }, account["token"])
        org_id = org["organization_id"]
        request("POST", f"/organizations/{org_id}/verification/approve", token=admin_token)
    account.update(login(account["email"], DEMO_PASSWORD))
    profile_changes = {
        "organization_name": "[DEMO] " + name,
        "description": "Fictional test organization. Sample information for trying the CareLife workflow; not a real provider.",
        "location": city + ", Bangladesh",
        "contact": "+880 1700 000 000",
    }
    if kind == "daycare":
        profile_changes.update({
            "capacity": 36,
            "age_range": "2–6 years",
            "opening_hours": "Sunday–Thursday, 8:00 am–5:00 pm",
            "facilities": "DEMO: supervised activities, meals, rest space, family updates",
            "fees": "DEMO: sample fees; confirm directly with the provider",
        })
    request("PATCH", f"/organizations/{org_id}/profile", profile_changes, account["token"])
    return org_id


def main():
    admin_password = getpass("CareLife admin password: ")
    admin_token = login("carelife@gmail.com", admin_password)["token"]
    suffix = sys.argv[1] if len(sys.argv) > 1 else secrets.token_hex(3)

    parent = signup(suffix, "parent", "parent_guardian", 1001)
    daycare_staff = make_staff(suffix, admin_token, "daycare_staff", "daycare.staff", 1002)
    orphanage_staff = make_staff(suffix, admin_token, "orphanage_staff", "orphanage.staff", 1003)
    care_home_staff = make_staff(suffix, admin_token, "care_home_staff", "carehome.staff", 1004)
    caregiver = signup(suffix, "caregiver", "independent_caregiver", 1005)
    donor = signup(suffix, "donor", "donor_supporter", 1006)
    family = signup(suffix, "family", "family_representative", 1007)

    daycare_id = register_org(daycare_staff, admin_token, "Little Steps Daycare", "daycare", "Uttara, Dhaka", 23.8759, 90.3795, 1)
    orphanage_id = register_org(orphanage_staff, admin_token, "Shapla Children’s Home", "orphanage", "Rajshahi", 24.3745, 88.6042, 2)
    care_home_id = register_org(care_home_staff, admin_token, "Shanti Care Home", "elderly_care", "Chattogram", 22.3569, 91.7832, 3)

    child_rows = request("GET", "/children/daycare", token=parent["token"])
    child = next((item for item in child_rows if item["full_name"] == "Nila Demo"), None)
    if not child:
        child = request("POST", "/children/daycare", {
            "full_name": "Nila Demo", "date_of_birth": "2020-09-25", "gender": "Female",
            "allergies": "DEMO: none listed", "medical_notes": "DEMO profile. No real child information.",
        }, parent["token"])
    enrollment_rows = request("GET", "/enrollments", token=parent["token"])
    enrollment = next((item for item in enrollment_rows if item["child_id"] == child["id"] and item["daycare_organization_id"] == daycare_id), None)
    if not enrollment:
        enrollment = request("POST", "/enrollments", {"child_id": child["id"], "daycare_organization_id": daycare_id}, parent["token"])
    if enrollment["status"] == "pending":
        enrollment = request("POST", f"/enrollments/{enrollment['id']}/review", {
            "status": "approved", "message": "DEMO enrollment approved for workflow testing.",
        }, daycare_staff["token"])
    attendance_rows = request("GET", f"/daycare/children/{child['id']}/attendance", token=parent["token"])
    attendance = attendance_rows[0] if attendance_rows else request("POST", "/daycare/attendance/check-in", {"enrollment_id": enrollment["id"]}, daycare_staff["token"])
    daily_updates = request("GET", f"/daycare/children/{child['id']}/daily-updates", token=parent["token"])
    if not daily_updates:
        request("POST", f"/daycare/children/{child['id']}/daily-updates", {
            "notes": "DEMO daily feed: Nila joined a group activity, ate lunch, rested after lunch, and was settled and cheerful this afternoon.",
        }, daycare_staff["token"])
    contacts = request("GET", f"/children/daycare/{child['id']}/emergency-contacts", token=parent["token"])
    if not contacts:
        request("POST", f"/children/daycare/{child['id']}/emergency-contacts", {
            "full_name": "DEMO Parent Contact", "relationship_to_child": "Parent",
            "phone": "+8801700001001", "email": parent["email"],
        }, parent["token"])

    caregivers = []
    for index in range(1, 7):
        account = caregiver if index == 1 else signup(suffix, f"caregiver{index:02d}", "independent_caregiver", 1000 + index)
        try:
            request("GET", "/caregivers/me/profile", token=account["token"])
        except RuntimeError:
            request("POST", "/caregivers/me/profile", {
                "service_type": "nanny" if index % 2 else "elder_care_giver",
                "bio": f"DEMO caregiver {index} profile for testing. Fictional example, pending CareLife review.",
                "experience_years": index + 1,
                "location": ["Uttara, Dhaka", "Sylhet", "Rajshahi", "Chattogram", "Khulna", "Dhaka"][index - 1],
            }, account["token"])
        caregivers.append(account)

    campaigns = request("GET", f"/organizations/{orphanage_id}/donation-campaigns", token=orphanage_staff["token"])
    campaign = next((item for item in campaigns if item["title"] == "DEMO: Classroom reading corner"), None)
    if not campaign:
        campaign = request("POST", f"/organizations/{orphanage_id}/donation-campaigns", {
        "title": "DEMO: Classroom reading corner",
        "description": "Fictional sample campaign to test campaign and impact workflows. No real funds are requested.",
        "target_amount": "25000.00", "currency": "BDT", "is_active": True,
        }, orphanage_staff["token"])
    needs = request("GET", f"/organizations/{orphanage_id}/donation-needs", token=orphanage_staff["token"])
    need = next((item for item in needs if item["title"] == "DEMO: Story books"), None)
    if not need:
        need = request("POST", f"/organizations/{orphanage_id}/donation-needs", {
        "title": "DEMO: Story books", "description": "Fictional in-kind need for testing the pledge flow.",
        "category": "Education", "need_type": "in_kind", "target_quantity": "20", "unit": "books", "is_active": True,
        }, orphanage_staff["token"])
    pledges = request("GET", "/my/in-kind-pledges", token=donor["token"])
    pledge = next((item for item in pledges if item["need_id"] == need["id"]), None)
    if not pledge:
        pledge = request("POST", f"/donation-needs/{need['id']}/in-kind-pledges", {
            "quantity": 3, "notes": "DEMO pledge only; no real goods are being delivered.",
        }, donor["token"])
    if pledge["status"] == "pledged":
        request("PATCH", f"/organizations/{orphanage_id}/in-kind-pledges/{pledge['id']}/status", {
            "status": "received",
        }, orphanage_staff["token"])
    updates = request("GET", f"/organizations/{orphanage_id}/impact-updates")
    update = next((item for item in updates if item["title"] == "DEMO: Reading corner prepared"), None)
    if not update:
        update = request("POST", f"/organizations/{orphanage_id}/impact-updates", {
        "title": "DEMO: Reading corner prepared",
        "content": "Fictional progress update for testing. The sample team arranged a reading corner and sorted donated story books. This record is demonstration content, not a report about a real organization.",
        }, orphanage_staff["token"])
    if update["status"] == "pending_review":
        request("POST", f"/admin/impact-updates/{update['id']}/review", {
            "decision": "approved", "privacy_confirmed": True,
            "review_notes": "DEMO sample approved for the public impact feed.",
        }, admin_token)

    residents = request("GET", f"/elder-care/organizations/{care_home_id}/residents", token=care_home_staff["token"])
    resident = next((item for item in residents if item["full_name"] == "DEMO Resident"), None)
    if not resident:
        resident = request("POST", f"/elder-care/organizations/{care_home_id}/residents", {
        "full_name": "DEMO Resident", "preferred_name": "Amma",
        "date_of_birth": "1945-05-10", "room_number": "DEMO-12",
        "emergency_contact_name": "DEMO Family Contact", "emergency_contact_phone": "+8801700001007",
        }, care_home_staff["token"])
    request("POST", f"/elder-care/organizations/{care_home_id}/residents/{resident['id']}/consent", {
        "family_representative_id": family["user_id"],
        "consent_granted": True,
    }, care_home_staff["token"])
    checkins = request("GET", f"/elder-care/residents/{resident['id']}/check-ins", token=family["token"])
    if not checkins:
        request("POST", f"/elder-care/residents/{resident['id']}/check-ins", {
            "wellbeing_status": "well", "notes": "DEMO family update: had tea, joined the garden walk, and is resting comfortably.",
        }, family["token"])

    print("DEMO SCENARIO CREATED")
    print("All accounts use the demo password: " + DEMO_PASSWORD)
    print("Data is fictional and labelled DEMO. No payment was charged.")
    for label, account in [
        ("Parent / guardian", parent), ("Daycare staff", daycare_staff),
        ("Orphanage staff", orphanage_staff), ("Care-home staff", care_home_staff),
        ("Donor / supporter", donor), ("Family representative", family),
    ]:
        print(f"{label}: {account['email']}")
    for index, account in enumerate(caregivers, start=1):
        print(f"Independent caregiver {index}: {account['email']}")
    print("Daycare organization ID: " + daycare_id)
    print("Children’s home organization ID: " + orphanage_id)
    print("Care-home organization ID: " + care_home_id)
    print("Child profile ID: " + child["id"])
    print("Enrollment ID: " + enrollment["id"])
    print("Attendance ID: " + attendance["id"])
    print("Impact update ID: " + update["id"])
    print("Resident ID: " + resident["id"])


if __name__ == "__main__":
    main()
