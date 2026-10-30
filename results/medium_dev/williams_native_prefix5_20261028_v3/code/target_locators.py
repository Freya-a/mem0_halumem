"""Review-only locators for old propositions and new-state evidence; semantic decisions are separate."""
OLD={
1:[r'Labrador'],2:[r'career change|career transition|mental health.*(work|job)|new (job|role)'],
3:[r'healthcare.*(access|underserved)|underserved|humanitarian'],4:[r'Susan'],5:[r'Daniel'],6:[r'Joshua'],
7:[r'looking for a new job|secured interviews and job offers|considering career change|career change is being considered'],8:[r'skydiv|extreme sport'],
9:[r'Earl Grey'],10:[r'Works at Historical.*Director'],11:[r'goal.*historically accurate films|career goal.*historically accurate films|collaborates with set dressers'],
12:[r'stress.*historical|historical accuracy demands|production schedules'],13:[r'stress.*historical|historical accuracy demands|production schedules|physically healthy'],
14:[r'Persian cats'],15:[r'Mary|Steven'],16:[r'classical symphon'],
17:[r'works at Blockchain.*senior developer|employed in the technology industry'],18:[r'works at Blockchain.*senior developer'],19:[r'17,?000'],
20:[r'role involves innovating new solutions|frequently contributes financially to political campaigns|life goal is to support the political career of a close relative'],21:[r'mental.*(stable|normal)|stable.*mental'],
22:[r'Sandra|Mary'],23:[r'Sandra|Mary'],24:[r'(launch|start).*firm|firm|clients']}
NEW={
1:[r'Golden Retriever'],2:OLD[2],3:[r'non.?profit|network|flexib'],4:[r'Susan'],5:[r'Daniel'],6:[r'Joshua'],
7:[r'transition|new (job|role)|work.life balance|healthier'],8:[r'simulat|skydiv|safety|new experience'],
9:[r'Earl Grey|tea house|nuanced taste'],10:[r'lead director.*Historical'],11:[r'creative control|innovation|innovative|authenticity'],
12:[r'improved mental|mental health.*improv|delegat|reduc.*stress'],13:[r'work.life balance.*improv|balance.*role change'],
14:[r'Persian|documentary|festival'],15:OLD[15],16:[r'Baroque|orchestra|music.*influenc'],
17:[r'political consult|transition|relative|seminar|professional'],18:[r'campaign|advis|consult'],19:[r'income|savings|expense'],
20:[r'data analy|communication|leadership|problem.solv|tech.*experience|experience.*tech'],21:[r'stress|mental health|income.*uncertain'],
22:[r'Sandra|Mary'],23:[r'Sandra|Mary|client|network'],24:[r'client|relie|milestone|achievement']}
