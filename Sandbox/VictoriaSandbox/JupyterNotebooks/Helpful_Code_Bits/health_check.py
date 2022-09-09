def is_healthy(name):
    med_words = ['cancer', 'cardiology', 'neurology', 'family care', 'pulmonary', 'anesthesia', 'orthope', 'urgent care', 'allergy', 'kidney', 'surgery', 'hosp', 'mri', 'throat', 'dentist', 'med', 'clinic', 'health', 'gastroenter','anesthesiologist','patient','physician','surgeon','doctor','hospital', 'md', 'medical', 'pediatrics', 'm.d.']
    healthy = False
    for word in med_words:
        if word in str(name).lower():
            healthy = True   
    return(healthy)