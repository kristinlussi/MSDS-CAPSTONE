import random
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os
from reportlab.platypus import PageBreak

# Fictional company names
def reset_insured_names():
    """Resets insured names list if it has been modified."""
    global INSURED_NAMES_POOL
    INSURED_NAMES_POOL = [
        "ABC Enterprises", "XYZ Industries", "Acme Corporation", "Global Solutions", "Premier Holdings",
        "United Systems", "Innovative Technologies", "Dynamic Ventures", "Pioneer Industries", "FutureTech Inc.",
        "Alpha Logistics", "Beta Manufacturing", "Gamma Services", "Delta Trading", "Epsilon Group",
        "Zeta Enterprises", "Omega Industries", "Vertex Solutions", "Summit Innovations", "Everest Enterprises",
        "Apex Technologies", "Beacon Systems", "Horizon Global", "Nexus Solutions", "Paramount Holdings",
        "Quantum Technologies", "Stellar Industries", "Vector Logistics", "BlueWave Systems", "Skyline Ventures",
        "Thunderbolt Manufacturing", "Infinity Solutions", "Stratosphere Enterprises", "Terra Firma Trading",
        "Momentum Holdings", "Velocity Innovations", "Titan Industries", "Helix Technologies", "Pulsar Enterprises",
        "Catalyst Solutions", "Vortex Systems", "NovaTech Inc.", "Synergy Global", "Cosmic Ventures",
        "Galactic Holdings", "Aurora Solutions", "Neon Technologies", "Fusion Enterprises", "Mirage Industries",
        "Neptune Logistics", "Solaris Systems", "Odyssey Innovations", "Lunar Holdings", "Zenith Enterprises",
        "AstroTech Solutions", "Orbit Industries", "Celestial Logistics", "Rocket Systems", "Meteor Innovations",
        "Eclipse Holdings", "Interstellar Enterprises", "Atlas Technologies", "Sonic Systems", "Cyclone Ventures",
        "Typhoon Trading", "StormFront Enterprises", "Blizzard Innovations", "Tundra Technologies", "Glacier Global",
        "Horizon Logistics", "Summit Manufacturing", "Elevate Systems", "Pinnacle Enterprises", "Aspire Solutions",
        "Envision Technologies", "Momentum Logistics", "Drive Innovations", "Rising Star Holdings", "New Dawn Industries",
        "Vertex Technologies", "Peak Systems", "Evolve Solutions", "Revolution Enterprises", "Quantum Logistics",
        "Echo Innovations", "Amplify Holdings", "Impact Systems", "Vanguard Technologies", "Trailblazer Enterprises",
        "Ironclad Industries", "Bulwark Holdings", "Titanium Solutions", "Fortress Systems", "Sentinel Technologies",
        "Guardian Global", "Protector Ventures", "Defender Innovations", "Aegis Enterprises", "Shield Technologies",
        "Palisade Solutions", "Bastion Holdings", "Stronghold Systems", "Reliance Logistics", "Trustworthy Technologies",
        "Endurance Enterprises", "Resilient Holdings", "EverSafe Solutions", "Unbreakable Industries", "Integrity Systems",
        "Steadfast Technologies", "Commitment Global", "Loyalty Holdings", "Perseverance Enterprises", "Foundation Systems",
        "Cornerstone Innovations", "Heritage Technologies", "Legacy Holdings", "Tradition Enterprises", "Pioneer Solutions",
        "Discovery Systems", "Explorer Technologies", "Navigator Enterprises", "Wayfinder Innovations", "Pathfinder Holdings",
        "Adventure Global", "Expedition Enterprises", "Odyssey Logistics", "Frontier Technologies", "Breakthrough Solutions",
        "Horizon Technologies", "Beyond Ventures", "Skyward Enterprises", "Limitless Innovations", "Unbound Holdings",
        "Boundless Systems", "Eternal Technologies", "Infinity Enterprises", "Continuum Solutions", "Singularity Global",
        "XYZ Innovations", "Alek Company", "Global Experiences", "Coffee Manufacturing", "Waters Incorporated",
        "Table Manufacturing Inc.", "Chair Builders Inc.", "Tree Solutions", "Plant Solutions",
        "Cheetoh Company", "Brooklyn Logistics"
    ]


def choose_sublimit(options, policy_limit, parent_limit=None):
    """
    Choose a sublimit option from a list of options
    - options: list containing numeric values (int or float) or strings (e.g. "Policy Limit")
    - policy_limit: overall policy limit (int)
    - parent_limit: if provided, also require option <= parent_limit (for interdependent sublimits)
    Returns the chosen option.
    """
    valid_options = []
    for option in options:
        if isinstance(option, (int, float)):
            if option <= policy_limit and (parent_limit is None or option <= parent_limit):
                valid_options.append(option)
        else:
            # Strings like "Policy Limit" are always allowed.
            valid_options.append(option)
    if not valid_options:
        # Fallback: if no option qualifies, simply use the policy limit.
        return policy_limit
    return random.choice(valid_options)

def choose_deductible(range_min, range_max, bias_min, bias_max, bias_probability=0.8):
    """
    Choose a deductible value with a bias toward the specified range.
    Values are in dollars -> result is rounded to the nearest thousand.
    """
    if random.random() < bias_probability:
        value = random.uniform(bias_min, bias_max)
    else:
        value = random.uniform(range_min, range_max)
    return round(value / 1000) * 1000

def choose_sir(range_min, range_max, bias_min, bias_max, bias_probability=0.8):
    """
    Choose a SIR value with bias, rounded to the nearest thousand.
    """
    if random.random() < bias_probability:
        value = random.uniform(bias_min, bias_max)
    else:
        value = random.uniform(range_min, range_max)
    return round(value / 1000) * 1000

def generate_policy_data(policy_id, insured_name, override_inception_date=None, is_renewal=False):
    """Generate single policy data with randomized sublimits, deductibles, SIR, and dates.
       If override_inception_date is provided, it is used as the inception date."""
    # Exclusion clause options
    TERRORISM_EXCLUSIONS = [
        """<b>Terrorism Exclusion Endorsement (NMA2920)</b><br/>
        Notwithstanding any provision to the contrary within this
        insurance or any endorsement thereto it is agreed that this
        insurance excludes loss, damage, cost or expense of whatsoever
        nature directly or indirectly caused by, resulting from or in
        connection with any act of terrorism regardless of any other
        cause or event contributing concurrently or in any other
        sequence to the loss.

        For the purpose of this endorsement an act of terrorism means
        an act, including but not limited to the use of force or
        violence and/or the threat thereof, of any person or group(s)
        of persons, whether acting alone or on behalf of or in
        connection with any organisation(s) or government(s),
        committed for political, religious, ideological or similar
        purposes including the intention to influence any government
        and/or to put the public, or any section of the public, in
        fear.

        This endorsement also excludes loss, damage, cost or expense
        of whatsoever nature directly or indirectly caused by,
        resulting from or in connection with any action taken in
        controlling, preventing, suppressing or in any way relating to
        any act of terrorism.

        If the Underwriters allege that by reason of this exclusion,
        any loss, damage, cost or expense is not covered by this
        insurance the burden of proving the contrary shall be upon the
        Assured.

        In the event any portion of this endorsement is found to be
        invalid or unenforceable, the remainder shall remain in full
        force and effect.
        """,

        """<b>Terrorism Exclusion Endorsement (NMA2921)</b><br/>
        Notwithstanding any provision to the contrary within this Policy or any endorsement thereto, it is agreed that this Policy
        excludes loss, damage, cost or expense of whatsoever nature directly or indirectly caused by, resulting from or in
        connection with any act of terrorism regardless of any other cause or event contributing concurrently or in any other
        sequence to the loss.
        For the purpose of this endorsement an act of terrorism means an act, including but not limited to the use of force or
        violence and/or the threat thereof, of any person or group(s) of persons, whether acting alone or on behalf of or in
        connection with any organization(s) or government(s), committed for political, religious, ideological or similar purposed
        including the intention to influence any government and/or to put the public, or any section of the public, in fear.
        This endorsement also excludes loss, damage, cost or expense of whatsoever nature directly or indirectly caused by,
        resulting from or in connection with any action taken in controlling, preventing, suppressing or in any way relating to any
        act of terrorism.
        If the Insurers allege that by reason of this exclusion, any loss, damage, cost or expense is not covered by this Policy the
        burden of proving the contrary shall be upon the Insured.
        In the event any portion of this endorsement is found invalid or unenforceable, the remainder shall remain in full force and
        Effect.
        """,

        """<b>Terrorism Exclusion Endorsement (NMA2918)</b><br/>
        Notwithstanding any provision to the contrary within this insurance or any
        endorsement thereto it is agreed that this insurance excludes loss, damage, cost or
        expense of whatsoever nature directly or indirectly caused by, resulting from or in
        connection with any of the following regardless of any other cause or event
        contributing concurrently or in any other sequence to the loss;
        1. war, invasion, acts of foreign enemies, hostilities or warlike operations (whether
        war be declared or not), civil war, rebellion, revolution, insurrection, civil
        commotion assuming the proportions of or amounting to an uprising, military or
        usurped power; or
        2. any act of terrorism.
        For the purpose of this endorsement an act of terrorism means an act, including
        but not limited to the use of force or violence and/or the threat thereof, of any
        person or group(s) of persons, whether acting alone or on behalf of or in
        connection with any organisation(s) or government(s), committed for political,
        religious, ideological or similar purposes including the intention to influence any
        government and/or to put the public, or any section of the public, in fear.
        This endorsement also excludes loss, damage, cost or expense of whatsoever
        nature directly or indirectly caused by, resulting from or in connection with any action
        taken in controlling, preventing, suppressing or in any way relating to 1 and/or 2
        above.
        If the Underwriters allege that by reason of this exclusion, any loss, damage, cost or
        expense is not covered by this insurance the burden of proving the contrary shall be
        upon the Assured.
        In the event any portion of this endorsement is found to be invalid or unenforceable,
        the remainder shall remain in full force and effect.
        """,

        """<b>Terrorism Exclusion Endorsement (NMA2919)</b><br/>
        Notwithstanding any provision to the contrary within this reinsurance or any endorsement thereto it is
        agreed that this reinsurance excludes loss, damage, cost or expense of whatsoever nature directly or
        indirectly caused by, resulting from or in connection with any of the following regardless of any other
        cause or event contributing concurrently or in any other sequence to the loss;
        (1) war, invasion, acts of foreign enemies, hostilities or warlike operations (whether war be declared or
        not), civil war, rebellion, revolution, insurrection, civil commotion assuming the proportions of or
        amounting to an uprising, military or usurped power; or
        (2) any act of terrorism.
        For the purpose of this exclusion, an act of terrorism means an activity, including the threat of an activity
        or the preparation for an activity, whether violent or nonviolent, that appears to be intended to
        (i) intimidate, coerce, or retaliate against any segment of the civilian population, or (ii) disrupt any
        segment of the economy, or (iii) influence the policy of a government by intimidation, coercion, or
        retaliation, or (iv) advance a political, religious, ideological, or ethnic cause.
        This endorsement also excludes loss, damage, cost or expense of whatsoever nature directly or
        indirectly caused by, resulting from or in connection with any action taken in controlling, preventing,
        suppressing or in any way relating to (1) and/or (2) above.
        In the event any portion of this endorsement is found to be invalid or unenforceable, the remainder
        shall remain in full force and effect.
        """,

        """<b>War & Civil War Exclusion Clause (NMA 464)</b><br/>
        Notwithstanding anything to the contrary contained herein this Policy does not cover Loss or Damage directly or indirectly occasioned by, happening through or in consequence of war, invasion, acts of foreign enemies, hostilities (whether war be declared or not), civil war, rebellion, revolution, insurrection, military or usurped power or confiscation or nationalism or requisition or destruction of or damage to property by or under the order of any government or public or local authority.
        """
]
    
    NUCLEAR_EXCLUSIONS = [
        'NMA 1975A Nuclear Energy Risk Exclusion', 
        'CL 370 Institute Radioactive Contamination, Chemical, Biological, Bio-Chemical, and Electromagnetic Weapons Exclusion Clause',
        'Excluded',
        'Included'
    ]
    COMMUNICABLE_DISEASE_EXCLUSIONS = [
        """<b>Communicable Disease Exclusion (LMA5394)</b><br/>
        1. Notwithstanding any provision to the contrary within this reinsurance agreement, this reinsurance
        agreement excludes any loss, damage, liability, claim, cost or expense of whatsoever nature,
        directly or indirectly caused by, contributed to by, resulting from, arising out of, or in connection
        with a Communicable Disease or the fear or threat (whether actual or perceived) of a
        Communicable Disease regardless of any other cause or event contributing concurrently or in any
        other sequence thereto.
        2. As used herein, a Communicable Disease means any disease which can be transmitted by means of
        any substance or agent from any organism to another organism where:
        2.1. the substance or agent includes, but is not limited to, a virus, bacterium, parasite or other
        organism or any variation thereof, whether deemed living or not, and
        2.2. the method of transmission, whether direct or indirect, includes but is not limited to,
        airborne transmission, bodily fluid transmission, transmission from or to any surface or
        object, solid, liquid or gas or between organisms, and
        2.3. the disease, substance or agent can cause or threaten damage to human health or human
        welfare or can cause or threaten damage to, deterioration of, loss of value of, marketability
        of or loss of use of property.
        """,

        """<b>Communicable Disease Endorsement (LMA5393)</b><br/>
        1. This policy, subject to all applicable terms, conditions and exclusions, covers losses attributable
        to direct physical loss or physical damage occurring during the period of insurance. Consequently
        and notwithstanding any other provision of this policy to the contrary, this policy does not insure
        any loss, damage, claim, cost, expense or other sum, directly or indirectly arising out of,
        attributable to, or occurring concurrently or in any sequence with a Communicable Disease or the
        fear or threat (whether actual or perceived) of a Communicable Disease.
        2. For the purposes of this endorsement, loss, damage, claim, cost, expense or other sum, includes,
        but is not limited to, any cost to clean-up, detoxify, remove, monitor or test:
        2.1. for a Communicable Disease, or
        2.2. any property insured hereunder that is affected by such Communicable Disease.
        3. As used herein, a Communicable Disease means any disease which can be transmitted by means of
        any substance or agent from any organism to another organism where:
        3.1. the substance or agent includes, but is not limited to, a virus, bacterium, parasite or other
        organism or any variation thereof, whether deemed living or not, and
        3.2. the method of transmission, whether direct or indirect, includes but is not limited to,
        airborne transmission, bodily fluid transmission, transmission from or to any surface or
        object, solid, liquid or gas or between organisms, and
        3.3. the disease, substance or agent can cause or threaten damage to human health or human
        welfare or can cause or threaten damage to, deterioration of, loss of value of, marketability
        of or loss of use of property insured hereunder.
        4. This endorsement applies to all coverage extensions, additional coverages, exceptions to any
        exclusion and other coverage grant(s).
        All other terms, conditions and exclusions of the policy remain the same.
        """,
        'Excluded',
        'Included'
    ]
    SANCTIONS_LIMITATIONS = [
        'LMA 3100 Sanctions Limitation & Exclusion Clause',
        'LMA 3100A Sanctions Limitation & Exclusion Clause',
        'Excluded',
        'Included'
    ]
    CYBER_EXCLUSIONS = [
        """<b>Cyber Exclusion Clause (LMA5401)</b><br/>
        1 Notwithstanding any provision to the contrary within this Policy or any endorsement thereto
        this Policy excludes any:
        1.1 Cyber Loss;
        1.2 loss, damage, liability, claim, cost, expense of whatsoever nature directly or indirectly
        caused by, contributed to by, resulting from, arising out of or in connection with any
        loss of use, reduction in functionality, repair, replacement, restoration or reproduction
        of any Data, including any amount pertaining to the value of such Data;
        regardless of any other cause or event contributing concurrently or in any other sequence
        thereto.
        2 In the event any portion of this endorsement is found to be invalid or unenforceable, the
        remainder shall remain in full force and effect.
        3 This endorsement supersedes and, if in conflict with any other wording in the Policy or any
        endorsement thereto having a bearing on Cyber Loss or Data, replaces that wording.
        Definitions
        4 Cyber Loss means any loss, damage, liability, claim, cost or expense of whatsoever nature
        directly or indirectly caused by, contributed to by, resulting from, arising out of or in
        connection with any Cyber Act or Cyber Incident including, but not limited to, any action
        taken in controlling, preventing, suppressing or remediating any Cyber Act or Cyber Incident.
        5 Cyber Act means an unauthorised, malicious or criminal act or series of related unauthorised,
        malicious or criminal acts, regardless of time and place, or the threat or hoax thereof
        involving access to, processing of, use of or operation of any Computer System.
        6 Cyber Incident means:
        6.1 any error or omission or series of related errors or omissions involving access to,
        processing of, use of or operation of any Computer System; or
        6.2 any partial or total unavailability or failure or series of related partial or total
        unavailability or failures to access, process, use or operate any Computer System.
        7 Computer System means:
        7.1 any computer, hardware, software, communications system, electronic device
        (including, but not limited to, smart phone, laptop, tablet, wearable device), server,
        cloud or microcontroller including any similar system or any configuration of the
        aforementioned and including any associated input, output, data storage device,
        networking equipment or back up facility,
        owned or operated by the Insured or any other party.
        8 Data means information, facts, concepts, code or any other information of any kind that is
        recorded or transmitted in a form to be used, accessed, processed, transmitted or stored by
        a Computer System.
        """,
        
        """<b>Cyber Exclusion Clause (LMA5400)</b><br/>
        1 Notwithstanding any provision to the contrary within this Policy or any endorsement thereto
        this Policy excludes any:
        1.1 Cyber Loss, unless subject to the provisions of paragraph 2;
        1.2 loss, damage, liability, claim, cost, expense of whatsoever nature directly or indirectly
        caused by, contributed to by, resulting from, arising out of or in connection with any
        loss of use, reduction in functionality, repair, replacement, restoration or reproduction
        of any Data, including any amount pertaining to the value of such Data, unless subject
        to the provisions of paragraph 3;
        regardless of any other cause or event contributing concurrently or in any other sequence
        thereto.
        2 Subject to all the terms, conditions, limitations and exclusions of this Policy or any
        endorsement thereto, this Policy covers physical loss or physical damage to property insured
        under this Policy caused by any ensuing fire or explosion which directly results from a Cyber
        Incident, unless that Cyber Incident is caused by, contributed to by, resulting from, arising
        out of or in connection with a Cyber Act including, but not limited to, any action taken in
        controlling, preventing, suppressing or remediating any Cyber Act.
        3 Subject to all the terms, conditions, limitations and exclusions of this Policy or any
        endorsement thereto, should Data Processing Media owned or operated by the Insured suffer
        physical loss or physical damage insured by this Policy, then this Policy will cover the cost to
        repair or replace the Data Processing Media itself plus the costs of copying the Data from
        back-up or from originals of a previous generation. These costs will not include research and
        engineering nor any costs of recreating, gathering or assembling the Data. If such media is
        not repaired, replaced or restored the basis of valuation shall be the cost of the blank Data
        Processing Media. However, this Policy excludes any amount pertaining to the value of such
        Data, to the Insured or any other party, even if such Data cannot be recreated, gathered or
        assembled.
        4 In the event any portion of this endorsement is found to be invalid or unenforceable, the
        remainder shall remain in full force and effect.
        5 This endorsement supersedes and, if in conflict with any other wording in the Policy or any
        endorsement thereto having a bearing on Cyber Loss, Data or Data Processing Media, replaces
        that wording.
        Definitions
        6 Cyber Loss means any loss, damage, liability, claim, cost or expense of whatsoever nature
        directly or indirectly caused by, contributed to by, resulting from, arising out of or in
        connection with any Cyber Act or Cyber Incident including, but not limited to, any action
        taken in controlling, preventing, suppressing or remediating any Cyber Act or Cyber Incident.
        7 Cyber Act means an unauthorised, malicious or criminal act or series of related unauthorised,
        malicious or criminal acts, regardless of time and place, or the threat or hoax thereof
        involving access to, processing of, use of or operation of any Computer System.
        8 Cyber Incident means:
        8.1 any error or omission or series of related errors or omissions involving access to,
        processing of, use of or operation of any Computer System; or
        8.2 any partial or total unavailability or failure or series of related partial or total
        unavailability or failures to access, process, use or operate any Computer System.
        9 Computer System means:
        9.1 any computer, hardware, software, communications system, electronic device
        (including, but not limited to, smart phone, laptop, tablet, wearable device), server,
        cloud or microcontroller including any similar system or any configuration of the
        aforementioned and including any associated input, output, data storage device,
        networking equipment or back up facility,
        owned or operated by the Insured or any other party.
        10 Data means information, facts, concepts, code or any other information of any kind that is
        recorded or transmitted in a form to be used, accessed, processed, transmitted or stored by
        a Computer System.
        11 Data Processing Media means any property insured by this Policy on which Data can be stored
        but not the Data itself.
        """,

        """<b>Marine Cyber Exclusion (LMA5402)</b><br/> 
        This clause shall be paramount and shall override anything in this insurance inconsistent therewith.
        1 In no case shall this insurance cover any loss, damage, liability or expense directly or indirectly caused by, contributed to by or arising from:
        1.1 the failure, error or malfunction of any computer, computer system, computer software programme, code, or process or any other electronic system, or
        1.2 the use or operation, as a means for inflicting harm, of any computer, computer system, computer software programme, malicious code, computer virus or process or any other electronic system.
        """,

        """<b>NMA 2915 Electronic Data Endorsement B</b><br/>
        Electronic Data Exclusion
        Notwithstanding any provision to the contrary within the Policy or any endorsement thereto, it is understood and agreed as follows:
        (a)  This Policy does not insure loss, damage, destruction, distortion, erasure, corruption or alteration of ELECTRONIC DATA from any cause whatsoever (including but not limited to COMPUTER VIRUS) or loss of use, reduction in functionality, cost, expense of whatsoever nature resulting therefrom, regardless of any other cause or event contributing concurrently or in any other sequence to the loss.
        ELECTRONIC DATA means facts, concepts and information converted to a form useable for communications, interpretation or processing by electronic and electromechanical data processing or electronically controlled equipment and includes programmes, software and other coded instructions for the processing and manipulation of data or the direction and manipulation of such equipment.
        COMPUTER VIRUS means a set of corrupting, harmful or otherwise unauthorised instructions or code including a set of maliciously introduced unauthorised instructions or code, programmatic or otherwise, that propagate themselves through a computer system or network of whatsoever nature. COMPUTER VIRUS includes but is not limited to 'Trojan Horses', 'worms' and 'time or logic bombs'.
        (b)  However, in the event that a peril listed below results from any of the matters described in paragraph (a) above, this Policy, subject to all its terms, conditions and exclusions, will cover physical damage occurring during the Policy period to property insured by this Policy directly caused by such listed peril.
        Listed Perils
        Fire Explosion
        Electronic Data Processing Media Valuation
        Notwithstanding any provision to the contrary within the Policy or any endorsement thereto, it is understood and agreed as follows:
        Should electronic data processing media insured by this Policy suffer physical loss or damage insured by this Policy, then the basis of valuation shall be the cost of the blank media plus the costs of copying the ELECTRONIC DATA from back-up or from originals of a previous generation. These costs will not include research and engineering nor any costs of recreating, gathering or assembling such ELECTRONIC DATA. If the media is not repaired, replaced or restored the basis of valuation shall be the cost of the blank media. However this Policy does not insure any amount pertaining to the value of such ELECTRONIC DATA to the Assured or any other party, even if such ELECTRONIC DATA cannot be recreated, gathered or assembled.
        """,
        'Excluded',
        'Included'
    ]

    MICROORGANISM_CLAUSES = [
        """<b>Microorganism Exclusion (LMA5018)</b><br/>
        This Policy does not insure any loss, damage, claim, cost, expense or other sum directly or indirectly arising out of or relating to:
        mold, mildew, fungus, spores or other microorganism of any type, nature, or description, including but not limited to any substance whose presence poses an actual or potential threat to human health.
        This Exclusion applies regardless whether there is (i) any physical loss or damage to insured property; (ii) any insured peril or cause, whether or not contributing concurrently or in any sequence; (iii) any loss of use, occupancy, or functionality; or (iv) any action required, including but not limited to repair, replacement, removal, cleanup, abatement, disposal, relocation, or steps taken to address medical or legal concerns.
        This Exclusion replaces and supersedes any provision in the Policy that provides insurance, in whole or in part, for these matters.
        """,

        """<b>Microorganism Exclusion (MAP)</b><br/>
        This policy does not insure any loss, damage, claim, cost, expense or other sum directly or indirectly arising out of or relating to:
        Mold, mildew, fungus, spores or other microorganisms of any type, nature, or description, including but not limited to any substance whose presence poses an actual or potential threat to human health.
        This exclusion applies regardless where there is
        any physical loss or damage to insured property ;
        any insured peril or cause, whether or not contributing concurrently or in any sequence ;
        any loss or use, occupancy or functionality or
        any action required including but not limited to repair, replacement, removal, cleanup, abatement, disposal, relocation, or steps taken to address medical or legal concerns.
        This exclusion replaces and supersedes any provision in the Policy that provides insurance, in whole or in part for this matters.
        """
]

    TRANSMISSION_LINES_EXCLUSION = ["""<b>Transmission and Distribution Lines Exclusion</b><br/>
        All transmission and distribution lines, including wire, cables, poles, pylons, standards, towers and any equipment of any type which may be attendant to such installations of any description. This exclusion includes but is not limited to transmission or distribution of electrical power, telephone or telegraph signals, and all communication signals whether audio or visual
        This exclusion applies only to above and below ground equipment, except that which is within three hundred and five (305) metres (or one thousand (1,000) feet) of the insured`s premises or as defined in the Assured`s original policy(ies)
        This exclusion applies both to physical loss or damage to the equipment and all business interruption, consequential loss and/or other contingent losses related to transmission and distribution lines
        """,
        "Included",
        "Excluded"]

    PREMIUM_PROCESSING_CLAUSE_TEMPLATE = """<b>Premium Processing Clause</b><br/>
        Where the premium is to be paid through {company_name}, payment to (Re)Insurers will be deemed to occur on the day ...
        """
    
    PREMIUM_PAYMENT_CLAUSE_TEMPLATE = """<b>Premium Payment Clause</b><br/>
        The (Re)Insured undertakes that premium will be paid in full to underwriters within {days} days of inception of this policy (or, in respect of instalment premiums, when due).
        If the premium due under this policy has not been so paid to Underwriters by the {days} day from the inception of this policy (and, in respect of instalment premiums, by the date they are due) Underwriters shall have the right to cancel this policy by notifying the (Re)Insured via the broker in writing. In the event of cancellation, premium is due to Underwriters on a pro rata basis for the period that Underwriters are on risk but the full policy premium shall be payable to Underwriters in the event of a loss or occurrence prior to the date of termination which gives rise to a valid claim under this policy.
        It is agreed that Underwriters shall give not less than 15 days prior notice of cancellation to the (Re)Insured via the broker. If premium due is paid in full to Underwriters before the notice period expires, notice of cancellation shall automatically be revoked. If not, the policy shall automatically terminate at the end of the notice period.
        Unless otherwise agreed, the Leading Underwriter (and Agreement Parties if appropriate) are authorized to exercise rights under this clause on their own behalf and on behalf of all Underwriters participating in this contract.
        If any provision of this clause is found by any court or administrative body of competent jurisdiction to be invalid or unenforceable, such invalidity or unenforceability will not effect the other provisions of this clause which will remain in full force and effect.
        Where the premium is to be paid through a London Market Bureau, payment to Underwriters will be deemed to occur on the day of delivery of a premium advice note to the Bureau."""

    PAYMENT_TERMS = [90, 150, 210]
    POLICY_DURATIONS = [12, 15, 18, 24]

    BROKERAGE_COMPANIES = ["Brokerage ABC", "ABC Brokers", "Random Brokers", "Brokerage Brokerage"]
    
    # Chooses policy duration (majority being 12 months)
    duration_months = random.choices(POLICY_DURATIONS, weights=[70, 10, 10, 10])[0]
    
    # Determine inception date.
    if override_inception_date:
        inception_date = override_inception_date
    else:
        days_back = random.randint(30, 360)
        initial_date = datetime.now() - timedelta(days=days_back)
        year = initial_date.year
        month = initial_date.month
        # Choose a start day: 1st, 15th, or last day of the month.
        start_day_option = random.choice([1, 15, 'last'])
        if start_day_option == 'last':
            start_day = calendar.monthrange(year, month)[1]
        else:
            start_day = start_day_option
        inception_date = datetime(year, month, start_day)
        if inception_date > initial_date:
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            if start_day_option == 'last':
                start_day = calendar.monthrange(year, month)[1]
            inception_date = datetime(year, month, start_day)
    
    # Expiration date: calculated from inception date + duration (in months)
    expiration_date = inception_date + relativedelta(months=+duration_months)
    
    # Overall policy limit (ensuring sublimits are valid)
    policy_limit = random.randint(10_000_000, 200_000_000)
    
    # Financial values
    insured_value = policy_limit * random.uniform(0.8, 1.2)
    base_premium = policy_limit * random.uniform(0.001, 0.005)
    brokerage_commission = random.uniform(0.10, 0.25)
    premium = base_premium * (1 + brokerage_commission)
    
    # Generate deductibles (rounded to the nearest thousand)
    deductible_all_other = choose_deductible(25_000, 50_000_000, 25_000, 50_000_000, bias_probability=0.5)
    deductible_earthquake = choose_deductible(5_000_000, 100_000_000, 5_000_000, 25_000_000)
    deductible_named_windstorm = choose_deductible(5_000_000, 100_000_000, 5_000_000, 25_000_000)
    deductible_flood = choose_deductible(5_000_000, 100_000_000, 5_000_000, 25_000_000)
    
    deductibles = {
        'all_other_loss': f"${deductible_all_other:,} each and every loss",
        'earthquake': f"${deductible_earthquake:,} each and every loss",
        'named_windstorm': f"${deductible_named_windstorm:,} each and every loss",
        'flood': f"${deductible_flood:,} each and every loss"
    }
    
    # Generate Self-Insured Retention (SIR)
    sir_choice = random.choices(['none', 'single', 'aggregated'], weights=[0.5, 0.3, 0.2])[0]
    if sir_choice == 'none':
        sir = None
    elif sir_choice == 'single':
        sir_value = choose_sir(5_000_000, 100_000_000, 5_000_000, 25_000_000)
        sir = f"${sir_value:,} each and every loss"
    else:  # Aggregated SIR
        sir_value = choose_sir(5_000_000, 100_000_000, 5_000_000, 25_000_000)
        aggregate = random.randint(sir_value, 100_000_000)
        aggregate = round(aggregate / 1000) * 1000
        sir = f"${sir_value:,} each and every loss and ${aggregate:,} in the annual aggregate"
    
    # Generate sublimits (all values must be <= policy_limit)
    sublimits = {}
    # Flood sublimit options (in dollars)
    flood_options = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    flood_sublimit = choose_sublimit(flood_options, policy_limit)
    sublimits['flood'] = f"${flood_sublimit:,}" if isinstance(flood_sublimit, (int, float)) else flood_sublimit

    # SFHA Flood: must be <= Flood sublimit
    sfha_flood_options = [5_000_000, 10_000_000, 25_000_000, 50_000_000]
    sfha_flood_sublimit = choose_sublimit(sfha_flood_options, policy_limit, parent_limit=(flood_sublimit if isinstance(flood_sublimit, (int, float)) else policy_limit))
    sublimits['sfha_flood'] = f"${sfha_flood_sublimit:,}" if isinstance(sfha_flood_sublimit, (int, float)) else sfha_flood_sublimit

    # Earthquake: options include "Policy Limit" or specific amounts.
    earthquake_options = ["Policy Limit", 50_000_000, 100_000_000, 200_000_000]
    earthquake_sublimit = choose_sublimit(earthquake_options, policy_limit)
    sublimits['earthquake'] = f"${earthquake_sublimit:,}" if isinstance(earthquake_sublimit, (int, float)) else earthquake_sublimit

    # California Earthquake: must be <= Flood sublimit.
    california_eq_options = [20_000_000, 25_000_000, 25_000_000, 50_000_000, 75_000_000, 100_000_000]
    california_eq_sublimit = choose_sublimit(california_eq_options, policy_limit, parent_limit=(flood_sublimit if isinstance(flood_sublimit, (int, float)) else policy_limit))
    sublimits['california_earthquake'] = f"${california_eq_sublimit:,}" if isinstance(california_eq_sublimit, (int, float)) else california_eq_sublimit

    # Named Windstorm: options include "Policy Limit".
    named_windstorm_options = ["Policy Limit", 50_000_000, 100_000_000, 200_000_000]
    named_windstorm_sublimit = choose_sublimit(named_windstorm_options, policy_limit)
    sublimits['named_windstorm'] = f"${named_windstorm_sublimit:,}" if isinstance(named_windstorm_sublimit, (int, float)) else named_windstorm_sublimit

    # Accidental Interruption of Services
    accidental_interruption_options = [10_000_000, 25_000_000, 50_000_000]
    accidental_interruption_sublimit = choose_sublimit(accidental_interruption_options, policy_limit)
    sublimits['accidental_interruption'] = f"${accidental_interruption_sublimit:,}" if isinstance(accidental_interruption_sublimit, (int, float)) else accidental_interruption_sublimit

    # Ammonia Contamination
    ammonia_contamination_options = [10_000_000, 25_000_000, 50_000_000]
    ammonia_contamination_sublimit = choose_sublimit(ammonia_contamination_options, policy_limit)
    sublimits['ammonia_contamination'] = f"${ammonia_contamination_sublimit:,}" if isinstance(ammonia_contamination_sublimit, (int, float)) else ammonia_contamination_sublimit

    # Automatic Coverage
    automatic_coverage_options = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    automatic_coverage_sublimit = choose_sublimit(automatic_coverage_options, policy_limit)
    sublimits['automatic_coverage'] = f"${automatic_coverage_sublimit:,}" if isinstance(automatic_coverage_sublimit, (int, float)) else automatic_coverage_sublimit

    # Contingent Time Element
    contingent_time_options = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    contingent_time_sublimit = choose_sublimit(contingent_time_options, policy_limit)
    sublimits['contingent_time_element'] = f"${contingent_time_sublimit:,}" if isinstance(contingent_time_sublimit, (int, float)) else contingent_time_sublimit

    # Errors & Omissions
    errors_omissions_options = [10_000_000, 25_000_000, 50_000_000]
    errors_omissions_sublimit = choose_sublimit(errors_omissions_options, policy_limit)
    sublimits['errors_omissions'] = f"${errors_omissions_sublimit:,}" if isinstance(errors_omissions_sublimit, (int, float)) else errors_omissions_sublimit

    # Gross Profits (period options)
    gross_profits_options = [12, 18]
    gross_profits = random.choice(gross_profits_options)
    sublimits['gross_profits'] = f"{gross_profits} months"

    # Ingress / Egress
    ingress_egress_options = [10_000_000, 25_000_000, 50_000_000]
    ingress_egress_sublimit = choose_sublimit(ingress_egress_options, policy_limit)
    sublimits['ingress_egress'] = f"${ingress_egress_sublimit:,}" if isinstance(ingress_egress_sublimit, (int, float)) else ingress_egress_sublimit

    # Miscellaneous Property
    misc_property_options = [10_000_000, 25_000_000, 50_000_000]
    misc_property_sublimit = choose_sublimit(misc_property_options, policy_limit)
    sublimits['miscellaneous_property'] = f"${misc_property_sublimit:,}" if isinstance(misc_property_sublimit, (int, float)) else misc_property_sublimit

    # Ordinary Payroll (fixed)
    sublimits['ordinary_payroll'] = "365 days"

    # Rental Property
    rental_property_options = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    rental_property_sublimit = choose_sublimit(rental_property_options, policy_limit)
    sublimits['rental_property'] = f"${rental_property_sublimit:,}" if isinstance(rental_property_sublimit, (int, float)) else rental_property_sublimit

    # Rolling Stock
    rolling_stock_options = [10_000_000, 25_000_000, 50_000_000]
    rolling_stock_sublimit = choose_sublimit(rolling_stock_options, policy_limit)
    sublimits['rolling_stock'] = f"${rolling_stock_sublimit:,}" if isinstance(rolling_stock_sublimit, (int, float)) else rolling_stock_sublimit

    # Transportation
    transportation_options = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    transportation_sublimit = choose_sublimit(transportation_options, policy_limit)
    sublimits['transportation'] = f"${transportation_sublimit:,}" if isinstance(transportation_sublimit, (int, float)) else transportation_sublimit

    # Valuable Papers & Records
    valuable_papers_options = [10_000_000, 25_000_000, 50_000_000, 100_000_000]
    valuable_papers_sublimit = choose_sublimit(valuable_papers_options, policy_limit)
    sublimits['valuable_papers_records'] = f"${valuable_papers_sublimit:,}" if isinstance(valuable_papers_sublimit, (int, float)) else valuable_papers_sublimit

    # Coverage options 
    coverage = {
        'earthquake': random.choice([True, False]),
        'strikes_riots_civil_commotion': random.choice([True, False]),
        'named_windstorm': random.choice([True, False]),
        'flood': random.choice([True, False])
    }
    
    # Generates policy number
    policy_number = f"PN-{random.randint(100000, 999999)}"
    
    return {
        'policy_id': policy_id,
        'insured_name': insured_name,
        'policy_number': policy_number,
        'terrorism_exclusion': random.choice(TERRORISM_EXCLUSIONS),
        'nuclear_exclusion': random.choice(NUCLEAR_EXCLUSIONS),
        'communicable_disease_exclusion': random.choice(COMMUNICABLE_DISEASE_EXCLUSIONS),
        'sanctions_limitation': random.choice(SANCTIONS_LIMITATIONS),
        'cyber_exclusion': random.choice(CYBER_EXCLUSIONS),
        'microorganism_exclusion': random.choice(MICROORGANISM_CLAUSES),
        'transmission_exclusion': random.choice(TRANSMISSION_LINES_EXCLUSION),
        'inception_date': inception_date.strftime('%Y-%m-%d'),
        'expiration_date': expiration_date.strftime('%Y-%m-%d'),
        'duration_months': duration_months,
        'policy_limit': f"${policy_limit:,}",
        'insured_value': f"${round(insured_value):,}",
        'premium': f"${round(premium):,}",
        'brokerage_commission_percentage': f"{round(brokerage_commission * 100, 2)}%",
        'payment_terms_days': random.choice(PAYMENT_TERMS),
        'deductibles': deductibles,
        'sir': sir,
        'sublimits': sublimits,
        'coverage': coverage
    }

def create_pdf(policy_data, output_dir='policies', is_renewal=False):
    """Create PDF document for a single policy using filename: 'Insured Name @ MM-DD-YYYY.pdf'."""
    os.makedirs(output_dir, exist_ok=True)
    # Convert inception_date to desired MM-DD-YYYY format for file naming.
    inception_dt = datetime.strptime(policy_data['inception_date'], '%Y-%m-%d')
    inception_str = inception_dt.strftime('%m-%d-%Y')
    # File name is: "Insured Name @ Inception Date.pdf"
    filename = f"{output_dir}/{policy_data['insured_name']} @ {inception_str}.pdf"
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    ))
    
    content = []
    policy_type = "RENEWAL" if is_renewal else "ORIGINAL"  # Note: You can customize this as needed.
    content.append(Paragraph(f"INSURANCE POLICY - {policy_type}", styles['CustomHeading']))
    content.append(Spacer(1, 12))
    
    # Policy Information Section (including Insured Name and Policy Number)
    policy_info = [
        ['Policy Number:', policy_data['policy_number']],
        ['Insured Name:', policy_data['insured_name']],
        ['Inception Date:', policy_data['inception_date']],
        ['Expiration Date:', policy_data['expiration_date']],
        ['Duration:', f"{policy_data['duration_months']} months"],
        ['Payment Terms:', f"{policy_data['payment_terms_days']} days from inception"],
        ['Policy Limit:', policy_data['policy_limit']]
    ]
    t = Table(policy_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    
    # Financial Information Section
    content.append(Paragraph("Financial Information", styles['Heading2']))
    content.append(Spacer(1, 12))
    financial_info = [
        ['Insured Value:', policy_data['insured_value']],
        ['Premium:', policy_data['premium']],
        ['Brokerage Commission:', policy_data['brokerage_commission_percentage']]
    ]
    t = Table(financial_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    
    # Deductibles Section
    content.append(Paragraph("Deductibles", styles['Heading2']))
    content.append(Spacer(1, 12))
    deductible_info = [[k.replace('_',' ').title() + ":", v] for k, v in policy_data['deductibles'].items()]
    t = Table(deductible_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    
    # Self Insured Retention (SIR) Section
    content.append(Paragraph("Self Insured Retention (SIR)", styles['Heading2']))
    content.append(Spacer(1, 12))
    sir_text = policy_data['sir'] if policy_data['sir'] else "None"
    content.append(Paragraph(sir_text, styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Sublimits Section
    content.append(Paragraph("Sublimits", styles['Heading2']))
    content.append(Spacer(1, 12))
    sublimit_info = [[k.replace('_',' ').title() + ":", v] for k, v in policy_data['sublimits'].items()]
    t = Table(sublimit_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    
    # Exclusions and Clauses Section
    # Function to format exclusion text properly
    def format_exclusion_text(text):
        """Splits long exclusions into multiple paragraphs."""
        paragraphs = [Paragraph(p.strip(), styles['Normal']) for p in text.split("<br/>")]
        return paragraphs

    # Append exclusions with wrapped text and new pages if needed
    content.append(Paragraph("Exclusions and Clauses", styles['Heading2']))
    content.append(Spacer(1, 12))

    for label, exclusion in [
        ("Terrorism", policy_data['terrorism_exclusion']),
        ("Nuclear", policy_data['nuclear_exclusion']),
        ("Communicable Disease", policy_data['communicable_disease_exclusion']),
        ("Cyber", policy_data['cyber_exclusion']),
        ("Sanctions", policy_data['sanctions_limitation']),
        ("Microorganism", policy_data['microorganism_exclusion']),
        ("Transmission & Distribution Lines", policy_data['transmission_exclusion'])
    ]:
        content.append(Paragraph(f"<b>{label}:</b>", styles['Heading3']))
        content.extend(format_exclusion_text(exclusion))
        content.append(Spacer(1, 12))
        content.append(PageBreak())  # Move each exclusion to a new page if too long
    
    # Coverage Information Section
    content.append(Paragraph("Coverage Information", styles['Heading2']))
    content.append(Spacer(1, 12))
    coverage_info = [
        ['Earthquake:', 'Included' if policy_data['coverage']['earthquake'] else 'Excluded'],
        ['Strikes, Riots, Civil Commotion:', 'Included' if policy_data['coverage']['strikes_riots_civil_commotion'] else 'Excluded'],
        ['Named Windstorm:', 'Included' if policy_data['coverage']['named_windstorm'] else 'Excluded'],
        ['Flood:', 'Included' if policy_data['coverage']['flood'] else 'Excluded']
    ]
    t = Table(coverage_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Reduce font size slightly
        ('WORDWRAP', (0, 1), (-1, -1), 'CJK')  # Ensures wrapping in second column
    ]))
    content.append(t)
    
    doc.build(content)
    return filename

def generate_all_policies(num_pairs=150):
    """Generate PDF documents for policy pairs (expiring and corresponding renewal).
       - For each pair, the expiring and renewal policies share the same Insured Name.
       - The renewal policy's inception date is set equal to the expiring policy's expiration date.
       - The expiring policy is from the previous year relative to the renewal."""
    output_dir = 'policies'
    reset_insured_names()
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    
    for i in range(1, num_pairs + 1):
        # Picks a unique insured name from the pool
        if INSURED_NAMES_POOL:
            insured_name = INSURED_NAMES_POOL.pop(0)
        else:
            insured_name = f"Company {i}"
        
        # Generate the expiring policy (original)
        expiring_policy = generate_policy_data(policy_id=i, insured_name=insured_name, override_inception_date=None, is_renewal=False)
        # Generate PDF for expiring policy
        expiring_filename = create_pdf(expiring_policy, output_dir)
        generated_files.append(expiring_filename)
        
        # For the renewal, override the inception date to be the expiring policy's expiration date.
        renewal_inception_dt = datetime.strptime(expiring_policy['expiration_date'], '%Y-%m-%d')
        renewal_policy = generate_policy_data(
            policy_id=num_pairs + i,  # Ensure a different policy number
            insured_name=insured_name,
            override_inception_date=renewal_inception_dt,
            is_renewal=True
        )
        renewal_filename = create_pdf(renewal_policy, output_dir)
        generated_files.append(renewal_filename)
    
    return generated_files

# Code to generate all policy pairs
#generate_all_policies(35)
#print(f"Generated {len(generated_files)} policy documents in the 'policies' directory")