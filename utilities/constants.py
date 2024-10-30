
reproductive_rights_and_health = {
    "Reproductive Rights": """(women OR women\'s OR female) AND (health OR medical OR healthcare OR "health care") AND ("reproductive health" OR "maternal health" OR "prenatal care" OR "postnatal care" OR "menstrual health" OR "menopause" OR "breast cancer" OR "cervical cancer" OR "ovarian cancer" OR "contraception" OR "family planning" OR "birth control" OR "pregnancy" OR "childbirth" OR "obstetrics" OR "gynecology" OR "sexual health" OR "STI" OR "STD" OR "HIV" OR "mental health" OR "depression" OR "anxiety" OR "eating disorders" OR "heart disease" OR "osteoporosis" OR "autoimmune disorders" OR "endometriosis" OR "PCOS" OR "fibroids" OR "hormone therapy" OR "mammography" OR "pap smear" OR "healthcare access"  OR "maternal mortality" OR "breastfeeding")"""
}

economic_equality =  {
    "Economic Equality": """((women OR women's OR female) AND (economic OR financial OR wage OR pay OR labor OR employment)) AND (equality OR empowerment OR discrimination OR gap OR "equal pay" OR "wage discrimination" OR "pay gap" OR "maternity leave" OR "parental leave" OR entrepreneur OR "business owner" OR "women-owned" OR childcare OR "workplace discrimination" OR STEM OR "sexual harassment" OR retirement OR pension OR leadership OR executive OR "gender diversity" OR "unpaid labor" OR "financial literacy")"""
}

safety_and_security = {
    "Safety and Security": """'(women OR women's OR female) AND (safety OR security OR protection OR violence OR abuse OR harassment) AND ("domestic violence" OR "intimate partner violence" OR "sexual assault" OR "sexual harassment" OR "workplace safety" OR "human trafficking" OR "sex trafficking" OR "safe transportation" OR "public safety" OR "online harassment" OR "cyberstalking" OR "stalking" OR "genital mutilation" OR "honor killing" OR "forced marriage" OR "reproductive rights" OR "bodily autonomy" OR "victim protection" OR "shelter" OR "safe house" OR "rape prevention" OR "self-defense" OR "campus safety" OR "night safety" OR "gender-based violence")'"""
}

topics = [reproductive_rights_and_health, economic_equality, safety_and_security]


us_states = [
    "US/Federal", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]