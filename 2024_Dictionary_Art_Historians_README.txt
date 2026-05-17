READ ME
—-


Project Name: Dictionary of Art Historians
URL: https://arthistorians.info
Date: 12/20/2023


Project Description: The Dictionary of Art Historians is a free, privately funded biographical dictionary of historians of western art written and maintained by scholars for the benefit of the public. It became associated with the Department of Art, Art History, and Visual Studies of Duke University in January of 2010. From 2016 on, it has been sponsored by the Duke Digital Art History & Visual Culture Research Lab. Initially conceived as a methodologic tool for English-language readers, the Dictionary of Art Historians compiles the documented facts of an historian’s life, post-retirement or posthumously, in order to serve as a background for understanding a specific text and the historiography of art. The DAH was begun in the fall of 1986 as a notecard project by indexing the historians cited in Eugene Kleinbauer’s Research “Guide to the History of Western Art” (1982) and his “Modern Perspectives in Western Art History” (1971), Heinrich Dilly’s “Kunstgeschichte als Institution” (1979) and some of Kultermann’s “Geschichte der Kunstgeschichte” (1966), now in translation as “The History of Art History” (1993). In 1996 the Dictionary was input electronically and in 2002 migrated to the internet. In 2018, the project underwent a major redesign and is again in active development, supported by Duke University’s Digital Art History & Visual Culture Research Lab, of which it is now a part. Subjects selected for inclusion are based solely by their reference in the historiographic literature (see bibliography link) and are not the selection of the editors. In 2023 the dictionary moved from a Drupal space to a WordPress space. This switch will see changes such as the addition of Getty vocabulary and images of the historians. In addition to a change in platform, there’s also been a specification in which art historians we’re currently focusing on. Researchers are actively searching for Black and female art historians to add to the Dictionary.

Data Sources: The data accompanying this file has been researched and developed over multiple iterations of the project since the late 1980s. Each entry should be considered scholarship in its own right and cited as such. The accompanying data was most recently structured and downloaded from the project website. The website is currently running WordPress version 6.4.2, and we used the plugin All Export to create the file attached. Some modifications were made to the order of columns and to data formatting to ensure that they follow the dictionary below. Fields that contain HTML have retained their coding. Empty fields reflect opportunities for  research to be done. This data is continually updated and added to, so future iterations may fill in these empty fields. If information has been researched and is not known to the researchers, 'unknown' is used, as in the case of dates of death and birth.


Data Dictionary:


Field Name:    WordPress Unique ID
Field Definition:    Unique identifier automatically assigned by WordPress.
Format Guidelines:    n/a
WordPress Field Name:    id
WordPress Field Type:    id
Dublin Core Equivalent:    identifier
Controlled Vocabulary:    n/a


Field Name:    Drupal Unique ID
Field Definition:    Contains legacy Node ID from Drupal website. Do not use for new entries in Wordpress. This field is not visible in the Art Historians editing template.
Format Guidelines:    
WordPress Field Name:    drupal_unique_id
WordPress Field Type:    Plain Number
Dublin Core Equivalent:    identifier
Controlled Vocabulary:    n/a


Field Name:    URL
Field Definition:    Slug pointing to the specific entry, e.g. "/abbottj"
Format Guidelines:    /[lastf] If the slug already exists for another entry, include the year of birth, e.g. /[lastf-YYYY]
WordPress Field Name:    url
WordPress Field Type:    url
Dublin Core Equivalent:    relation
Controlled Vocabulary:    n/a


Field Name:    Directory
Field Definition:    First initial of the art historian's last name.
Format Guidelines:    [A]
WordPress Field Name:    directory
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    relation
Controlled Vocabulary:    n/a


Field Name:    Title
Field Definition:    Established name of the art historian.
Format Guidelines:    
• Form that appears in English.
• As listed in Oxford Dictionary of National Biography or other reference(s) or version most published.
• [Last, First Middle], e.g. "Miller, Dorothy Canning". • If only first initial(s) is/are given: [Last, F.], e.g. "Miller, D." or "Miller, D. C.".
• If no middle name is given: [Last, First], e.g. "Miller, Dorothy".
• If only a middle initial is given: [Last, First M.], e.g. "Miller, Dorothy C."
• If only one name is given: [Name], e.g. "Aristotle".
WordPress Field Name:    title
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    title
Controlled Vocabulary:    n/a
    
Field Name:    Full Name
Field Definition:    Established name of the art historian.
Format Guidelines:    
• Form that appears in English.
• As listed in Oxford Dictionary of National Biography or other reference(s) or version most published.
• [Last, First Middle], e.g. "Miller, Dorothy Canning". • If only first initial(s) is/are given: [Last, F.], e.g. "Miller, D." or "Miller, D. C.".
• If no middle name is given: [Last, First], e.g. "Miller, Dorothy".
• If only a middle initial is given: [Last, First M.], e.g. "Miller, Dorothy C."
• If only one name is given: [Name], e.g. "Aristotle".
WordPress Field Name:    full_name
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    title
Controlled Vocabulary:    n/a
    
Field Name:    Other Names
Field Definition:    Art historian's translations, aliases, sobriquets, variations, etc. One name per field.
Format Guidelines:    [First Middle Last]
WordPress Field Name:    other_names
WordPress Field Type:    Plain Text (repeatable)
Dublin Core Equivalent:    title
Controlled Vocabulary:    n/a
    
Field Name:    Birth Approximation
Field Definition:    For entering modifiers such as c., fl., before, after, etc.
Format Guidelines:    
• Use "c." for "circa" if exact date or year is uncertain, e.g. [c. 1800].
• If an artist is known to have been born or died before or after a specific date, use "before," e.g. [before 1660] or "after," e.g. [after 1660] to indicate this.
• If a birth date is not available but an active date is, use "fl." for "flourished, e.g. [fl. 1550].
• If a year falls prior to the common era (C.E. or A.D.), format the date as YYYY B.C.E., e.g. [500 B.C.E.].
WordPress Field Name:    birth_approximation
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Birth Day
Field Definition:    Day the art historian was born.
Format Guidelines:    [DD], e.g. "01" or "13". If a range, [DD-DD], e.g. "01-04". If unknown, leave blank.
WordPress Field Name:    birth_days
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Birth Month
Field Definition:    Month the art historian was born.
Format Guidelines:    [Month], e.g. "January". If a range is known: [Month-Month], e.g. "March-April". If unknown, leave blank.
WordPress Field Name:    birth_months
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Birth Year
Field Definition:    Year the art historian was born.
Format Guidelines:    [YYYY], e.g. "1901". Use "c." for "circa" if exact date or year is uncertain, e.g. "c. 1800". If an artist is known to have been born or died before or after a specific date, use "before," e.g. “before 1660” or "after," e.g. “after 1660” to indicate this. If a birth date is not available but an active date is, use "fl." for "flourished, e.g. “fl. 1550”. If a year falls prior to the common era (C.E. or A.D.), format the date as [YYYY B.C.E.], e.g. “500 B.C.E.” If a birth or death date is not known or not found in existing documentation, enter "unknown" in the year field. If a date is disputed in sources, include the date range and an explanation of different dates and their sources in the Overview and/or Notes fields.
WordPress Field Name:    birth_years
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Death Approximation
Field Definition:    For entering modifiers such as c., fl., before, after, etc.
Format Guidelines:    
• Use "c." for "circa" if exact date or year is uncertain, e.g. [c. 1800].
• If an artist is known to have been born or died before or after a specific date, use "before," e.g. [before 1660] or "after," e.g. [after 1660] to indicate this.
• If a birth date is not available but an active date is, use "fl." for "flourished, e.g. [fl. 1550].
• If a year falls prior to the common era (C.E. or A.D.), format the date as YYYY B.C.E., e.g. [500 B.C.E.].
WordPress Field Name:    death_approximation
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Death Day
Field Definition:    Day the art historian died.
Format Guidelines:    [DD], e.g. "01" or "13". If a range, [DD-DD], e.g. "01-04". If unknown, leave blank.
WordPress Field Name:    death_days
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Death Month
Field Definition:    Month the art historian died.
Format Guidelines:    [Month], e.g. "January". If a range is known: [Month-Month], e.g. "March-April". If unknown, leave blank.
WordPress Field Name:    death_months
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Death Year
Field Definition:    Year the art historian died.
Format Guidelines:    [YYYY], e.g. "1901". Use "c." for "circa" if exact date or year is uncertain, e.g. "c. 1800". If an artist is known to have been born or died before or after a specific date, use "before," e.g. “before 1660” or "after," e.g. “after 1660” to indicate this. If a birth date is not available but an active date is, use "fl." for "flourished, e.g. “fl. 1550”. If a year falls prior to the common era (C.E. or A.D.), format the date as [YYYY B.C.E.], e.g. “500 B.C.E.” If a birth or death date is not known or not found in existing documentation, enter "unknown" in the year field. If a date is disputed in sources, include the date range and an explanation of different dates and their sources in the Overview and/or Notes fields.
WordPress Field Name:    death_years
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    date
Controlled Vocabulary:    n/a


Field Name:    Place Born
Field Definition:    Location the art historian was born.
Format Guidelines:   
• [City, County or State, Country], e.g. "Boston, MA, USA" or "Howth, County Dublin, Ireland".
• If only a region is known: [Region, Country], e.g. "England, UK".
• If a neighborhood or borough is known: [Neighborhood, City, State, Country], e.g. "Brooklyn, New York, NY, United States".
• If the place name during the person's life time is different from the present day place name, list the historic place name in the Place Born Notes field.
WordPress Field Name:    place_born
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    coverage
Controlled Vocabulary:    Getty Thesaurus of Geographic Names, World-Historical Gazetteer, GeoNames


Field Name:    Place Born Notes
Field Definition:    For details about place that do not fit taxonomy, e.g. "on a ship in the South Pacific Ocean".
Format Guidelines:    Short description to appear after any selected Place taxonomy. If no Place taxonomy is selected, this short description should include all relevant details in as brief a description as possible.
WordPress Field Name:    place_born_notes
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    coverage
Controlled Vocabulary:    n/a


Field Name:    Place Died
Field Definition:    Location the art historian died.
Format Guidelines:    
• [City, County or State, Country], e.g. "Boston, MA, USA" or "Howth, County Dublin, Ireland".
• If only a region is known: [Region, Country], e.g. "England, UK".
• If a neighborhood or borough is known: [Neighborhood, City, State, Country], e.g. "Brooklyn, New York, NY, United States".
• If the place name during the person's life time is different from the present day place name, list the historic place name in the Place Died Notes field.
WordPress Field Name:    place_died
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    coverage
Controlled Vocabulary:    Getty Thesaurus of Geographic Names, World-Historical Gazetteer, GeoNames


Field Name:    Place Died Notes
Field Definition:    For details about place that do not fit taxonomy, e.g. "Flanders Fields".
Format Guidelines:    Short description to appear after any selected Place taxonomy. If no Place taxonomy is selected, this short description should include all relevant details in as brief a description as possible.
WordPress Field Name:    place_died_notes
WordPress Field Type:    Plain Text
Dublin Core Equivalent:    coverage
Controlled Vocabulary:    n/a


Field Name:    Home Country
Field Definition:    Name of country/ies in which art historian lived, or was exiled to.
Format Guidelines:    [Country], e.g. "France".
WordPress Field Name:    home_country
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    coverage
Controlled Vocabulary:    Getty Thesaurus of Geographic Names, World-Historical Gazetteer, GeoNames


Field Name:    Gender
Field Definition:    Name of gender with which art historian was known to identify based on scholarly documentation or self-reporting.
Format Guidelines:    Single word/phrase, e.g. "female", "transgender", "two-spirit," or "male".
WordPress Field Name:    gender
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    description
Controlled Vocabulary:    Homosaurus


Field Name:    Subject Area
Field Definition:    Disciplinary area(s) in which art historian published and/or held expertise.
Format Guidelines:    Single word or phrase, e.g. "eighteenth-century" or "painting".
WordPress Field Name:    subject_area
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    subject
Controlled Vocabulary:    Getty Art & Architecture Thesaurus


Field Name:    Career
Field Definition:    Name of the career(s) art historian held.
Format Guidelines:    Single word or phrase, e.g. "curator" or "professor".
WordPress Field Name:    career
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    subject
Controlled Vocabulary:    Getty Art & Architecture Thesaurus


Field Name:    Institution
Field Definition:    Name of institution(s) art historian was associated with, especially those where they spent the majority of their career.
Format Guidelines:    "Authoritative name used by the institution itself in the institution's primary language, e.g. "Metropolitan Museum of Art" or "École Nationale des Chartes". When in doubt, use the title referred to on Wikipedia."
WordPress Field Name:    institution
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    coverage
Controlled Vocabulary:    Wikipedia, Wikidata


Field Name:    Overview
Field Definition:    Narrative of the art historian's life and work.
Format Guidelines:    First sentence is a fragment stating major (art-historical) importance. The paragraph(s) that follow(s) includes biographical information, links to known art historians in the Dictionary if applicable, relevant work, notable publications, etc.
WordPress Field Name:    overview
WordPress Field Type:    WYSIWYG (Visual Editor)
Dublin Core Equivalent:    description
Controlled Vocabulary:    n/a


Field Name:    Selected Bibliography
Field Definition:    Selected list of art historian's publications and projects.
Format Guidelines:    Unordered list. Chicago Manual of Style.
WordPress Field Name:    selected_bibliography
WordPress Field Type:    WYSIWYG (Visual Editor)
Dublin Core Equivalent:    relation
Controlled Vocabulary:    n/a


Field Name:    Sources
Field Definition:    Source(s) from which information about the art historian is derived.
Format Guidelines:    Unordered list. Chicago Manual of Style.
WordPress Field Name:    sources
WordPress Field Type:    WYSIWYG (Visual Editor)
Dublin Core Equivalent:    source
Controlled Vocabulary:    n/a


Field Name:    Archives
Field Definition:    List of archives containing art historian's materials.
Format Guidelines:    Unordered list. Chicago Manual of Style.
WordPress Field Name:    archives
WordPress Field Type:    WYSIWYG (Visual Editor)
Dublin Core Equivalent:    relation
Controlled Vocabulary:    n/a


Field Name:    Contributors
Field Definition:    Author(s) and editor(s) of the art historian's entry as they wish to be named.
Format Guidelines:    [First Middle Last]
WordPress Field Name:    contributor
WordPress Field Type:    Taxonomy
Dublin Core Equivalent:    contributor
Controlled Vocabulary:    n/a


Field Name:    Notes
Field Definition:    Miscellaneous bucket for uncertainties & internal notes about dates/places.
Format Guidelines:    Phrases or short sentences. Include references here if citing specific conflicting/uncertain information. Please include any information about conflicting or uncertain information here that is not included in the full entry. These notes are only visible to the editor and web content manager.
WordPress Field Name:    notes
WordPress Field Type:    WYSIWYG (Visual Editor)
Dublin Core Equivalent:    description
Controlled Vocabulary:    n/a


Field Name:    Date Last Modified
Field Definition:    The date and time at which the entry was last modified in the website. Automatically generated by WordPress.
Format Guidelines:    n/a
WordPress Field Name:    date
WordPress Field Type:    date
Dublin Core Equivalent:    date
Controlled Vocabulary:    ISO 8601