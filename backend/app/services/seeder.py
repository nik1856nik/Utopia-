from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from ..models.project import Project, Event
from ..models.issue import Issue
from ..models.field import FieldSubmission

def seed_data(s: Session):
    if s.query(Project).count() > 0:
        return
    
    today = date(2026, 10, 10)
    
    rows = [
        # --- 4 JOBS IN TRIPLICANE (600005) ---
        (
            'CG-TRIP-01', 'Triplicane High Road Stormwater Drain Reconstruction', 'Drainage', 'Stormwater Drainage',
            'Triplicane', '600005', 'Triplicane High Road · Triplicane',
            'Demolish undersized brick drain and construct modern RCC monsoon storm conduit to prevent water stagnation.',
            'In progress', 65, 14200000, 'AquaWorks Infrastructure Ltd.', '2026-07-20', 13.0585, 80.2751,
            'Lane 1 closed · 9am–5pm', None, None,
            4, 'Er. K. Ramanathan', '+91 94440 28192', 'ee.zone10@chennaicorporation.gov.in',
            'AquaWorks Infrastructure', '+91 98841 55210',
            'Heavy excavation window: 22:00 – 04:00 (Acoustic shields installed)',
            'Sprinklers operational: 08:30 – 13:30',
            True, 'Traffic diverted via Bells Road and Wallajah Road'
        ),
        (
            'CG-TRIP-02', 'Pycrafts Road Underground 11kV Feeder Cable Modernization', 'Electricity', 'TANGEDCO',
            'Triplicane', '600005', 'Pycrafts Road (Bharathi Salai) · Triplicane',
            'Replace ageing overhead 11kV cables with armored underground trenches and install feeder pillar boxes.',
            'In progress', 88, 8500000, 'VoltCity Power Systems', '2026-09-15', 13.0560, 80.2730,
            'Footpath restricted · Single lane flow', None, None,
            6, 'Er. Anitha Selvan', '+91 94458 55102', 'aee.triplicane@tangedco.gov.in',
            'VoltCity Power Systems', '+91 98840 99881',
            'Cable pulling generator sound: 21:00 – 02:00 (Silencer mounted)',
            'Minimal dust (Trench restoration phase)',
            True, 'Single lane movement near Ice House junction'
        ),
        (
            'CG-TRIP-03', 'Parthasarathy Car Street Water Main Replacement', 'Water supply', 'Chennai Metro Water',
            'Triplicane', '600005', 'Car Street · Parthasarathy Temple Environs',
            'Replace century-old corroded water mains with ductile iron pipes and smart isolation valves.',
            'Delayed', 42, 9800000, 'Southern HydroTech Ltd.', '2026-06-18', 13.0542, 80.2768,
            'Night water interruption · 11pm–3am', 'Heritage temple wall foundation inspection required ASI structural audit.',
            'Archaeological clearance received; twin micro-drilling crews deployed for rapid completion.',
            3, 'Dr. V. Meenakshi', '+91 94451 88301', 'ee.water.mylapore@metrowater.tn.gov.in',
            'Southern HydroTech Ltd.', '+91 98402 11299',
            'Silent rotary boring: 10:00 – 17:00 (Zero impact vibrators)',
            'Continuous water misting during pavement cutting',
            True, 'Pedestrian access maintained; two-wheelers diverted via Singarachari Street'
        ),
        (
            'CG-TRIP-04', 'Bells Road Bitumen Macadam Resurfacing & Tactile Walkway', 'Roads', 'Greater Chennai Corporation',
            'Triplicane', '600005', 'Bells Road · Near Chepauk Stadium',
            'Milling damaged carriageway, laying dense bituminous concrete, and constructing barrier-free pedestrian paths.',
            'Scheduled', 15, 6200000, 'Southline Civil Works', '2026-11-10', 13.0610, 80.2785,
            'Night resurfacing · 11pm–5am', None, None,
            2, 'Er. S. Radhakrishnan', '+91 94440 28192', 'ee.roads.central@chennaicorporation.gov.in',
            'Southline Civil Works', '+91 97909 44321',
            'Milling machine noise window: 23:00 – 04:30',
            'Vacuum sweeper truck deployed behind milling crew',
            True, 'Night traffic diversion via Victoria Hostel Road'
        ),

        # --- 5 JOBS IN MELAKOTTAIYYUR (600127) ---
        (
            'CG-MELA-01', 'Vandalur-Kelambakkam Expressway 6-Lane Expansion & Storm Culvert', 'Roads', 'State Highways & GCC',
            'Melakottaiyur', '600127', 'Vandalur-Kelambakkam Road · Melakottaiyur Corridor',
            'Major 6-lane road widening, dual concrete cross-culverts, and street lighting along expressway corridor.',
            'In progress', 72, 32000000, 'Apex Infra Projects', '2026-08-15', 12.8425, 80.1412,
            'Median lane blocked · 30 km/h speed limit', None, None,
            4, 'Er. S. Radhakrishnan', '+91 94440 28192', 'ee.highways.south@chennaicorporation.gov.in',
            'Apex Infra Projects', '+91 94450 12345',
            'Pneumatic compactor operations: 09:00 – 18:00',
            'Heavy earth hauling: 08:00 – 14:00 (Dedicated water tankers stationed)',
            True, 'Dual-lane bypass created on northern median'
        ),
        (
            'CG-MELA-02', 'Melakottaiyur Substation 33kV Line Extension & Trenching', 'Electricity', 'TANGEDCO',
            'Melakottaiyur', '600127', 'Melakottaiyur Main Road · Near Sports University',
            'Dedicated 33kV underground feeder cable route to meet rising academic and residential demand.',
            'In progress', 50, 11500000, 'VoltCity Projects', '2026-10-05', 12.8390, 80.1450,
            'Partial single-lane restriction · 10am–4pm', None, None,
            3, 'Er. Anitha Selvan', '+91 94458 55102', 'aee.substation@tangedco.gov.in',
            'VoltCity Projects', '+91 98840 99881',
            'Trench cutter sound: 10:00 – 16:00',
            'Dry earth excavation mist cannons: 09:00 – 13:00',
            True, 'Flagger crews guiding university campus shuttle traffic'
        ),
        (
            'CG-MELA-03', 'Melakottaiyur CMWSSB Drinking Water Pipeline Network Scheme', 'Water supply', 'Chennai Metro Water',
            'Melakottaiyur', '600127', 'Kandigai-Melakottaiyur Road Junction',
            'Pipelaying of 400mm ductile iron trunk line to connect suburban Melakottaiyur to Nemmeli desalination network.',
            'Delayed', 30, 19800000, 'AquaWorks Infrastructure', '2026-06-25', 12.8460, 80.1385,
            'Road narrowing near Kandigai junction', 'Granite bedrock strata encountered at 2.5m depth requiring hydraulic breakers.',
            'High-power hydraulic breaker deployed with acoustic sound blanket; work hours extended to twin shifts.',
            3, 'Dr. V. Meenakshi', '+91 94451 88301', 'ee.water.south@metrowater.tn.gov.in',
            'AquaWorks Infrastructure', '+91 98841 55210',
            'Rock breaking window: 22:00 – 04:00 (Acoustic enclosure in use)',
            'Wet slurry extraction active (Zero dry airborne dust)',
            True, 'Light vehicles only; heavy lorries diverted via Mambakkam Link'
        ),
        (
            'CG-MELA-04', 'Melakottaiyur Tech Corridor Fiber Optic Ducting', 'Telecommunications', 'Chennai Fibre Network',
            'Melakottaiyur', '600127', 'IIITDM Campus Outer Ring Road · Melakottaiyur',
            'Multi-operator underground micro-duct network connecting educational institutes and residential townships.',
            'Scheduled', 10, 5400000, 'MetroLink Utilities', '2026-11-25', 12.8375, 80.1420,
            'Footpath trenching only · Road open', None, None,
            2, 'Er. Rajesh Kumar', '+91 94443 11200', 'telecom.cord@chennaicorporation.gov.in',
            'MetroLink Utilities', '+91 98400 33119',
            'Micro-trenching cutter: 11:00 – 15:00',
            'Vacuum dust suction unit operational behind cutter',
            True, 'Normal vehicular corridor traffic unaffected'
        ),
        (
            'CG-MELA-05', 'Melakottaiyur Lake Bund Flood Protection & Cross Box Drainage', 'Drainage', 'Water Resources Dept',
            'Melakottaiyur', '600127', 'Melakottaiyur Lake Bund Road',
            'Reinforce lake bund embankments, build concrete revetments, and construct high-capacity cross drainage culverts.',
            'In progress', 85, 16300000, 'Southern Water Engineering', '2026-09-30', 12.8450, 80.1465,
            'Bund road restricted to local farm vehicles', None, None,
            5, 'Er. S. Radhakrishnan', '+91 94440 28192', 'wrd.chennaisouth@chennaicorporation.gov.in',
            'Southern Water Engineering', '+91 94442 77112',
            'Concrete vibrator & pump: 08:00 – 17:00',
            'Continuous misting along perimeter',
            True, 'Through traffic diverted to expressway link road'
        ),

        # --- 3 JOBS IN AYANAVARAM (600023) ---
        (
            'CG-AYAN-01', 'Ayanavaram Konnur High Road Sewer Trunk Main Overhaul', 'Sewerage', 'Chennai Metro Water',
            'Ayanavaram', '600023', 'Konnur High Road · Ayanavaram',
            'Trenchless micro-tunneling and sewer chamber structural rehabilitation along high-density Konnur High Road.',
            'In progress', 58, 17400000, 'CivicFlow Engineering Ltd.', '2026-07-28', 13.0970, 80.2350,
            'One lane open towards Otteri · 8am–7pm', None, None,
            4, 'Dr. V. Meenakshi', '+91 94451 88301', 'ee.water.north@metrowater.tn.gov.in',
            'CivicFlow Engineering', '+91 98410 44552',
            'De-watering bypass pump sound: continuous (Acoustic box installed)',
            'Trench vacuuming: 09:00 – 14:00',
            True, 'One-way traffic towards Otteri; buses diverted via Medavakkam Tank Road'
        ),
        (
            'CG-AYAN-02', 'Ayanavaram Bus Terminus Junction Improvement & Drainage', 'Road safety', 'Greater Chennai Corporation',
            'Ayanavaram', '600023', 'Medavakkam Tank Road · Near Ayanavaram Bus Depot',
            'Redesign junction geometry, build heavy-duty covered monsoon RCC drains, and create safe pedestrian islands.',
            'Delayed', 25, 12800000, 'Urban Axis Contractors', '2026-06-10', 13.0945, 80.2380,
            'Bus bays 1 & 2 temporarily shifted', 'High daytime bus movement restricted excavation to 4 hours per night.',
            'Joint MTC approval received for deploying additional night shift and pre-cast concrete drain boxes.',
            3, 'Er. K. Ramanathan', '+91 94440 28192', 'ee.roads.north@chennaicorporation.gov.in',
            'Urban Axis Contractors', '+91 94442 77112',
            'Jackhammering & crane ops: 23:30 – 04:00',
            'Dust mist barrier screens installed along depot perimeter',
            True, 'Buses enter via south gate; light vehicles unaffected'
        ),
        (
            'CG-AYAN-03', 'Ayanavaram Railway Colony Power Cable Modernization & Footpath', 'Electricity', 'TANGEDCO',
            'Ayanavaram', '600023', 'Railway Colony Road · Ayanavaram',
            'Underground cabling, replacement of rusted distribution pillars, and laying interlocking paver footpath.',
            'In progress', 92, 7300000, 'VoltCity Power Systems', '2026-09-22', 13.0995, 80.2315,
            'Footpath work in progress · Normal roadway', None, None,
            6, 'Er. Anitha Selvan', '+91 94458 55102', 'aee.ayanavaram@tangedco.gov.in',
            'VoltCity Power Systems', '+91 98840 99881',
            'Paving slab wet cutter: 10:00 – 16:00',
            'Tile cutting wet saw used (Zero airborne dust)',
            True, 'Normal vehicular traffic restored'
        ),

        # --- OTHER CHENNAI LANDMARK JOBS (T. Nagar, Mylapore, Adyar, Velachery) ---
        (
            'CG-2025-041', 'T. Nagar Stormwater Drain & Culvert Renewal', 'Drainage', 'Stormwater Drainage',
            'T. Nagar', '600017', 'Usman Road Corridor · T. Nagar',
            'Major replacement of ageing RCC drain sections and monsoon capacity augmentation along Usman Road.',
            'In progress', 68, 18400000, 'Chennai Metro Water Infra', '2026-07-12', 13.0418, 80.2337,
            'Lane 1 closed · 7am–6pm', 'Unmapped underground high-voltage utility cables encountered during mechanical excavation.',
            'TANGEDCO joint inspection completed; night shifting crew deployed to restore east lane in phases.',
            4, 'Er. K. Ramanathan', '+91 94440 28192', 'ee.zone10@chennaicorporation.gov.in',
            'AquaWorks Infrastructure', '+91 98841 55210',
            'Heavy pneumatic drilling allowed: 22:00 – 04:00 only (Sound curtains mounted)',
            'Excavation dust suppression sprinklers active: 09:00 – 14:00',
            True, 'Heavy vehicles diverted via Panagal Park and G.N. Chetty Road'
        ),
        (
            'CG-2026-021', 'T. Nagar Underground High-Speed Fibre Ducting', 'Telecommunications', 'Chennai Fibre Network',
            'T. Nagar', '600017', 'Usman Road Corridor · T. Nagar',
            'Install shared multi-operator underground telecom fibre ducts along the same corridor as the active stormwater drain.',
            'Scheduled', 0, 3900000, 'MetroLink Utilities', '2026-11-15', 13.0412, 80.2340,
            'Trenching & lane narrowing · 9am–5pm', None, None,
            2, 'Er. Rajesh Kumar', '+91 94443 11200', 'telecom.cord@chennaicorporation.gov.in',
            'MetroLink Utilities', '+91 98400 33119',
            'Micro-trenching cutter sound: 10:00 – 15:00',
            'Micro-trench vacuum unit active',
            True, 'Coordinated single-lane traffic flow with GCC'
        ),
        (
            'CG-2025-038', 'Mylapore Heritage Water Main & Valve Replacement', 'Water supply', 'Chennai Metro Water',
            'Mylapore', '600004', 'Luz Church Road · Mylapore',
            'Upgrade century-old cast iron water supply mains with high-pressure ductile iron pipes and smart isolation valves.',
            'Delayed', 54, 12600000, 'AquaWorks Infrastructure', '2026-06-02', 13.0368, 80.2676,
            'Night water interruption · 10pm–4am', 'Hard underground granite bedrock encountered at Luz junction, slowing trench boring.',
            'Advanced diamond rotary cutters deployed; 2 additional night shifts working through 25 October.',
            4, 'Dr. V. Meenakshi', '+91 94451 88301', 'ee.water.mylapore@metrowater.tn.gov.in',
            'Southern HydroTech Ltd.', '+91 98402 11299',
            'Rock breaking generator sound: 23:00 – 03:30 (Silenced acoustic housing)',
            'Slurry vacuum trucks operational: 08:30 – 12:00',
            True, 'Detour via Royapettah High Road and Karpagambal Nagar'
        ),
        (
            'CG-2026-012', 'Adyar Avenue Carriageway Resurfacing & Walkway', 'Roads', 'Greater Chennai Corporation',
            'Adyar', '600020', 'Lattice Bridge (LB) Road · Adyar',
            'Milling damaged carriageway, laying dense bituminous macadam, and constructing level tactile pedestrian walkways.',
            'Upcoming', 0, 9200000, 'Southline Civil Works', '2026-11-20', 13.0067, 80.2565,
            'Night resurfacing · 10pm–5am', None, None,
            2, 'Er. S. Radhakrishnan', '+91 94440 28192', 'ee.roads.adyar@chennaicorporation.gov.in',
            'Southline Civil Works', '+91 97909 44321',
            'Milling machine noise window: 23:00 – 04:00',
            'Asphalt smoke mitigation units deployed',
            True, 'Single lane alternation via Sardar Patel Road'
        ),
        (
            'CG-2026-015', 'Velachery Junction Drainage & Pedestrian Subway', 'Road safety', 'Greater Chennai Corporation',
            'Velachery', '600042', '100 Feet Bypass Road · Velachery',
            'Construct dedicated flood relief cross-drainage conduits and pedestrian safety barriers at Velachery junction.',
            'In progress', 35, 14300000, 'Urban Axis Contractors', '2026-12-08', 12.9815, 80.2180,
            'Partial lane restriction · 9am–4pm', None, None,
            3, 'Er. S. Radhakrishnan', '+91 94440 28192', 'ee.velachery@chennaicorporation.gov.in',
            'Urban Axis Contractors', '+91 94442 77112',
            'Concrete vibrator & excavator sound: 10:00 – 16:00',
            'Excavation dust misting cannons active',
            True, 'Heavy freight vehicles diverted via Inner Ring Road'
        )
    ]

    for (code, title, cat, dept, loc, pin, addr, desc, status_txt, prog, budget,
         contract, due, lat, lng, disruption, reason, mit, step, eng_name, eng_ph,
         eng_em, cont_co, cont_ph, noise_w, dust_w, gmaps_b, detour) in rows:
        
        start_d = today - timedelta(days=60 if prog > 0 else -14)
        due_d = date.fromisoformat(due)
        rev_d = date(2026, 10, 28) if status_txt == 'Delayed' else None

        p = Project(
            code=code, title=title, category=cat, department=dept, locality=loc, pincode=pin,
            address=addr, description=desc, status=status_txt, progress=prog, budget=budget,
            contractor=contract, start_date=start_d, due_date=due_d, revised_date=rev_d,
            lat=lat, lng=lng, disruption=disruption, delay_reason=reason, mitigation=mit,
            current_step=step, contact_engineer_name=eng_name, contact_engineer_phone=eng_ph,
            contact_engineer_email=eng_em, contact_contractor=cont_co, contact_contractor_phone=cont_ph,
            noise_warning=noise_w, dust_warning=dust_w, gmaps_broadcast=gmaps_b, detour_advice=detour
        )
        s.add(p)
        s.flush()

        events = [
            ('Administrative Sanction & DPR Cleared', 'Municipal clearance and budget sanction approved by Corporation council.', today - timedelta(days=90), True),
            ('Contractor Tenders Awarded', f'Execution contract awarded to {contract}.', today - timedelta(days=70), True),
        ]
        if prog > 0:
            events.append(('Excavation & Trenching Commenced', 'Mechanical trenching and safety barricades erected along street corridor.', today - timedelta(days=35), True))
        if prog >= 50:
            events.append(('Core Infrastructure Installation', 'Pipes / cables / culvert box sections successfully jointed.', today - timedelta(days=12), True))
        if status_txt == 'Completed':
            events.append(('Road Restoration & Final Inspection', 'High-grade bitumen laid; final site certificate issued.', today - timedelta(days=21), True))
        elif status_txt == 'Delayed':
            events.append(('Schedule Adjustment Recorded', f'Official delay notice logged: {reason}.', today - timedelta(days=4), True))

        for ev_title, ev_detail, ev_date, ev_ver in events:
            s.add(Event(project_id=p.id, title=ev_title, detail=ev_detail, created=datetime.combine(ev_date, datetime.min.time()), verified=ev_ver))

    # Seed public community questions with official answers
    seed_issues = [
        # Triplicane
        (
            'CGI-TRIP-001', 'CG-TRIP-01', '600005', 'Question regarding Drainage Lags',
            'Why is excavation taking longer on Triplicane High Road near the market? Will it be done before monsoon?',
            'Answered', 'Normal', 'Triplicane', True, True,
            'Excavation reached the outfall canal connection. Heavy culvert casting is completed; road backfilling is scheduled to finish by 20 October well before heavy rains.',
            datetime.utcnow() - timedelta(hours=22), 'Er. K. Ramanathan (GCC Zone 10)'
        ),
        (
            'CGI-TRIP-002', 'CG-TRIP-03', '600005', 'Question regarding Water Supply Interruption',
            'Will water tankers be provided during Car Street pipeline work on Saturday?',
            'Answered', 'Normal', 'Triplicane', True, True,
            'Static 9000L water tank stationed near Temple North Gate. Tanker supplies scheduled at 6 AM and 4 PM.',
            datetime.utcnow() - timedelta(hours=14), 'Dr. V. Meenakshi (Chennai Metro Water)'
        ),
        (
            'CGI-TRIP-003', 'CG-TRIP-02', '600005', 'Pycrafts Road Noise Complaint',
            'Generator for cable laying was running past 11:30 PM. Were residents intiminated?',
            'Resolved', 'Normal', 'Triplicane', False, False,
            'TANGEDCO night inspector verified sound curtains were missing. Contractor rectified housing with acoustic silencing blankets.',
            datetime.utcnow() - timedelta(days=2), 'Er. Anitha Selvan (TANGEDCO)'
        ),

        # Melakottaiyur
        (
            'CGI-MELA-001', 'CG-MELA-01', '600127', 'Question on Vandalur-Kelambakkam Lane Block',
            'Why is the road narrowed near the sports university? Are both directions open for college buses?',
            'Answered', 'Normal', 'Melakottaiyur', True, True,
            'Six-lane culvert expansion is ongoing. Two dedicated bypass lanes have been opened on the north flank with traffic police marshals.',
            datetime.utcnow() - timedelta(hours=18), 'Er. S. Radhakrishnan (State Highways & GCC)'
        ),
        (
            'CGI-MELA-002', 'CG-MELA-03', '600127', 'Question on Water Pipeline Work',
            'Is drinking water supply affected in Kandigai during pipe laying?',
            'Answered', 'Normal', 'Melakottaiyur', True, True,
            'Supply operates on alternate days between 5:30 AM and 8:30 AM without disruption. Pressure testing will only happen at midday.',
            datetime.utcnow() - timedelta(hours=10), 'Dr. V. Meenakshi (Chennai Metro Water)'
        ),
        (
            'CGI-MELA-003', 'CG-MELA-02', '600127', 'Dust Complaint near Campus',
            'Dry excavation earth creating dust plumes near university gate during morning hours.',
            'Resolved', 'High', 'Melakottaiyur', False, False,
            'Contractor deployed 2 additional mobile water mist cannons. Earth trucks now required to tarp load completely.',
            datetime.utcnow() - timedelta(days=1), 'Er. Anitha Selvan (TANGEDCO)'
        ),

        # Ayanavaram
        (
            'CGI-AYAN-001', 'CG-AYAN-01', '600023', 'Question regarding Konnur High Road Sewer Work',
            'Heavy sewage smell and dewatering noise near Konnur High Road at night. Is work permitted at night?',
            'Answered', 'Normal', 'Ayanavaram', True, True,
            'Acoustic insulation covers installed on bypass suction pumps. Work will wrap up within 5 days with bio-enzyme odor neutralizers.',
            datetime.utcnow() - timedelta(hours=12), 'Dr. V. Meenakshi (Chennai Metro Water)'
        ),
        (
            'CGI-AYAN-002', 'CG-AYAN-02', '600023', 'Question on Bus Terminus Access',
            'Bus bay 2 shifted at Ayanavaram depot causing congestion. When will concrete drain slab cure?',
            'Answered', 'Normal', 'Ayanavaram', True, True,
            'Rapid-hardening concrete was poured on Thursday. Bus bay 2 reopens on Monday morning following load certification.',
            datetime.utcnow() - timedelta(hours=6), 'Er. K. Ramanathan (GCC Roads)'
        )
    ]

    for ref, p_code, pin, kind, msg, st, sev, loc, is_q, int_adv, reply, rep_at, rep_by in seed_issues:
        matched_p = s.query(Project).filter_by(code=p_code).first()
        iss = Issue(
            ref=ref,
            project_id=matched_p.id if matched_p else None,
            department=matched_p.department if matched_p else "Greater Chennai Corporation",
            pincode=pin,
            kind=kind,
            message=msg,
            status=st,
            severity=sev,
            locality=loc,
            is_question=is_q,
            intimated_in_advance=int_adv,
            official_reply=reply,
            replied_at=rep_at,
            replied_by=rep_by
        )
        s.add(iss)

    # Seed field submissions
    p1 = s.query(Project).filter_by(code='CG-TRIP-01').first()
    p2 = s.query(Project).filter_by(code='CG-TRIP-02').first()
    
    seeds = [
        FieldSubmission(
            project_id=p1.id if p1 else 1,
            official_name="P. Murugan",
            official_badge="GCC-SITE-104",
            official_dept="Greater Chennai Corporation",
            report_type="progress",
            summary="Pre-cast box drain slab reinforcement & alignment inspected",
            detail="Zone 10 Triplicane High Road: Reinforcement spacing for 80m channel verified against GCC structural drawings. Concrete pour authorized.",
            progress_pct=65,
            step_number=4,
            status="Approved by Executive Engineer",
            labor_count=18,
            machinery_deployed="1x JCB Excavator, 1x 15-ton Transit Mixer, 2x Plate Compactors",
            shift_hours="Day Shift (08:30 - 17:30)",
            created=datetime.utcnow() - timedelta(hours=6)
        ),
        FieldSubmission(
            project_id=p2.id if p2 else 2,
            official_name="S. Kumar",
            official_badge="TNEB-SITE-312",
            official_dept="TANGEDCO",
            report_type="photo",
            summary="11kV Armored feeder cable pulling & trench sand bedding",
            detail="Pycrafts Road stretch: 300 sq.mm XLPE aluminum cable pulled smoothly into trench with 150mm river sand bedding and red protective warning tiles.",
            progress_pct=88,
            step_number=6,
            photo_url="https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=600&q=80",
            photo_caption="Underground 11kV Feeder Cable Bedding — Pycrafts Rd",
            status="Verified by Superintending Engineer",
            labor_count=12,
            machinery_deployed="1x Cable Winch, 1x Silent Generator",
            shift_hours="Night Shift (21:00 - 03:00)",
            created=datetime.utcnow() - timedelta(hours=14)
        )
    ]
    for fs in seeds:
        s.add(fs)

    s.commit()
