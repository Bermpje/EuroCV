# Europass CV XML Schema v3.4 Reference

This document provides a comprehensive reference for the Europass CV XML Schema version 3.4, based on the official documentation.

## Document Structure

### Root Element: `<Europass>`

```xml
<Europass xmlns="http://europass.cedefop.europa.eu/Europass" 
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://europass.cedefop.europa.eu/Europass
                              http://europass.cedefop.europa.eu/xml/EuropassSchema_V3.4.xsd">
  <DocumentInfo/>
  <LearnerInfo/>
</Europass>
```

## 1. DocumentInfo

Metadata about the Europass document.

```xml
<DocumentInfo>
  <DocumentType>ECV</DocumentType>  <!-- Europass CV -->
  <CreationDate>2024-01-15T10:30:00Z</CreationDate>
  <LastUpdateDate>2024-01-20T14:45:00Z</LastUpdateDate>
  <XSDVersion>V3.4</XSDVersion>
  <Generator>EuroCV v0.1.0</Generator>
  <Comment>Generated automatically</Comment>
</DocumentInfo>
```

### Fields:
- **DocumentType**: ECV (Europass CV), ELP (Europass Language Passport), ECL (Europass Cover Letter)
- **CreationDate**: ISO 8601 datetime
- **LastUpdateDate**: ISO 8601 datetime (optional)
- **XSDVersion**: Schema version (V3.0, V3.1, V3.2, V3.3, V3.4)
- **Generator**: Tool that generated the document
- **Comment**: Additional notes (optional)

## 2. LearnerInfo

Main container for CV content.

### 2.1 Identification

Personal information.

```xml
<Identification>
  <PersonName>
    <Title>Mr</Title>  <!-- Optional -->
    <FirstName>John</FirstName>
    <Surname>Doe</Surname>
  </PersonName>
  
  <ContactInfo>
    <Address>
      <Contact>
        <AddressLine>123 Main Street</AddressLine>
        <AddressLine>Apartment 4B</AddressLine>
        <PostalCode>1234AB</PostalCode>
        <Municipality>Amsterdam</Municipality>
        <Country>
          <Code>NL</Code>
          <Label>Netherlands</Label>
        </Country>
      </Contact>
    </Address>
    
    <Email>
      <Contact>john.doe@example.com</Contact>
    </Email>
    
    <Telephone>
      <Contact>+31 6 12345678</Contact>
      <Use>
        <Code>mobile</Code>
        <Label>Mobile</Label>
      </Use>
    </Telephone>
    
    <Website>
      <Contact>https://johndoe.com</Contact>
      <Use>
        <Code>personal</Code>
        <Label>Personal</Label>
      </Use>
    </Website>
    
    <InstantMessaging>
      <Contact>@johndoe</Contact>
      <Use>
        <Code>twitter</Code>
        <Label>Twitter</Label>
      </Use>
    </InstantMessaging>
  </ContactInfo>
  
  <Demographics>
    <Birthdate>
      <Year>1990</Year>
      <Month>--06</Month>
      <Day>---15</Day>
    </Birthdate>
    <Gender>
      <Code>M</Code>  <!-- M/F -->
      <Label>Male</Label>
    </Gender>
    <Nationality>
      <Code>NL</Code>
      <Label>Dutch</Label>
    </Nationality>
  </Demographics>
  
  <Photo>
    <MimeType>image/jpeg</MimeType>
    <Data>[Base64 encoded image data]</Data>
  </Photo>
</Identification>
```

### 2.2 Headline

Professional headline/title.

```xml
<Headline>
  <Type>
    <Code>preferred</Code>
    <Label>Preferred Job</Label>
  </Type>
  <Description>
    <Label>Senior Software Engineer</Label>
  </Description>
</Headline>
```

### 2.3 WorkExperience

Work history entries.

```xml
<WorkExperienceList>
  <WorkExperience>
    <Period>
      <From>
        <Year>2018</Year>
        <Month>--01</Month>
        <Day>---15</Day>
      </From>
      <To>
        <Year>2023</Year>
        <Month>--12</Month>
        <Day>---31</Day>
      </To>
      <Current>false</Current>
    </Period>
    
    <Position>
      <Code>2512</Code>  <!-- ISCO-08 code -->
      <Label>Software Developer</Label>
    </Position>
    
    <Activities>Led development of microservices architecture.
    Mentored junior developers.
    Implemented CI/CD pipelines.</Activities>
    
    <Employer>
      <Name>Tech Corp B.V.</Name>
      <ContactInfo>
        <Address>
          <Contact>
            <Municipality>Amsterdam</Municipality>
            <Country>
              <Code>NL</Code>
              <Label>Netherlands</Label>
            </Country>
          </Contact>
        </Address>
        <Website>
          <Contact>https://techcorp.nl</Contact>
        </Website>
      </ContactInfo>
      <Sector>
        <Code>J</Code>  <!-- NACE code -->
        <Label>Information and communication</Label>
      </Sector>
    </Employer>
  </WorkExperience>
</WorkExperienceList>
```

### ISCO-08 Occupation Codes (examples):
- 2512: Software developers
- 2513: Web and multimedia developers
- 2514: Applications programmers
- 2519: Software and applications developers not elsewhere classified
- 2521: Database designers and administrators
- 2522: Systems administrators
- 2523: Computer network professionals
- 1330: Information and communications technology services managers

### 2.4 Education

Education history.

```xml
<EducationList>
  <Education>
    <Period>
      <From>
        <Year>2016</Year>
        <Month>--09</Month>
      </From>
      <To>
        <Year>2020</Year>
        <Month>--06</Month>
      </To>
    </Period>
    
    <Title>Bachelor of Science in Computer Science</Title>
    
    <Skills>Key competencies acquired during studies.</Skills>
    
    <Activities>Member of student programming club.
    Participated in hackathons.</Activities>
    
    <Organisation>
      <Name>University of Amsterdam</Name>
      <ContactInfo>
        <Address>
          <Contact>
            <Municipality>Amsterdam</Municipality>
            <Country>
              <Code>NL</Code>
              <Label>Netherlands</Label>
            </Country>
          </Contact>
        </Address>
      </ContactInfo>
    </Organisation>
    
    <Level>
      <Code>6</Code>  <!-- ISCED 2011 level -->
      <Label>Bachelor or equivalent</Label>
    </Level>
  </Education>
</EducationList>
```

### ISCED 2011 Education Levels:
- 0: Early childhood education
- 1: Primary education
- 2: Lower secondary education
- 3: Upper secondary education
- 4: Post-secondary non-tertiary education
- 5: Short-cycle tertiary education
- 6: Bachelor or equivalent
- 7: Master or equivalent
- 8: Doctoral or equivalent

### 2.5 Skills

#### Communication / Linguistic Skills

```xml
<Skills>
  <Linguistic>
    <MotherTongue>
      <Description>
        <Code>nl</Code>  <!-- ISO 639-1 -->
        <Label>Dutch</Label>
      </Description>
    </MotherTongue>
    
    <ForeignLanguage>
      <Description>
        <Code>en</Code>
        <Label>English</Label>
      </Description>
      <ProficiencyLevel>
        <Listening>C2</Listening>
        <Reading>C2</Reading>
        <SpokenInteraction>C1</SpokenInteraction>
        <SpokenProduction>C1</SpokenProduction>
        <Writing>C1</Writing>
      </ProficiencyLevel>
      <Certificate>
        <Title>IELTS Academic</Title>
        <AwardingBody>British Council</AwardingBody>
        <Date>
          <Year>2019</Year>
        </Date>
        <Level>8.0</Level>
      </Certificate>
    </ForeignLanguage>
  </Linguistic>
```

### CEFR Language Levels:
- **A1**: Breakthrough - Basic user
- **A2**: Waystage - Basic user
- **B1**: Threshold - Independent user
- **B2**: Vantage - Independent user
- **C1**: Effective operational proficiency - Proficient user
- **C2**: Mastery - Proficient user

#### Other Skills

```xml
  <Communication>
    <Description>Excellent presentation and public speaking skills.
    Experience with technical documentation and reporting.</Description>
  </Communication>
  
  <Organisational>
    <Description>Project management using Agile/Scrum methodologies.
    Team leadership and coordination.</Description>
  </Organisational>
  
  <JobRelated>
    <Description>Full-stack web development.
    Cloud infrastructure management (AWS, Azure).
    Database design and optimization.</Description>
  </JobRelated>
  
  <Computer>
    <Description>Programming: Python, JavaScript, TypeScript, Java, Go
    Frameworks: React, FastAPI, Django, Spring Boot
    Tools: Docker, Kubernetes, Git, Jenkins
    Databases: PostgreSQL, MongoDB, Redis</Description>
  </Computer>
  
  <Driving>
    <Description>
      <Code>B</Code>  <!-- EU driving license category -->
      <Label>Driving License B</Label>
    </Description>
  </Driving>
  
  <Other>
    <Description>Photography, Video editing</Description>
  </Other>
</Skills>
```

### 2.6 Achievement

Achievements, publications, projects, etc.

```xml
<AchievementList>
  <Achievement>
    <Title>
      <Code>projects</Code>
      <Label>Projects</Label>
    </Title>
    <Description>Open-source contribution to FastAPI framework.
    Developed internal tooling for CI/CD automation.</Description>
  </Achievement>
  
  <Achievement>
    <Title>
      <Code>publications</Code>
      <Label>Publications</Label>
    </Title>
    <Description>"Microservices Architecture Best Practices"
    Published in: Tech Journal, 2022</Description>
  </Achievement>
  
  <Achievement>
    <Title>
      <Code>honors_awards</Code>
      <Label>Honors and Awards</Label>
    </Title>
    <Description>Employee of the Year 2022 - Tech Corp
    1st Place - National Hackathon 2020</Description>
  </Achievement>
</AchievementList>
```

### Achievement Types:
- projects
- publications
- presentations
- citations
- conferences
- seminars
- workshops
- membership
- honors_awards
- references

### 2.7 ReferenceTo

References to other documents.

```xml
<ReferenceTo>
  <Document>
    <Name>Portfolio</Name>
    <Description>Online portfolio showcasing projects</Description>
    <URL>https://johndoe.com/portfolio</URL>
  </Document>
  
  <Document>
    <Name>LinkedIn Profile</Name>
    <URL>https://linkedin.com/in/johndoe</URL>
  </Document>
  
  <Document>
    <Name>GitHub Profile</Name>
    <URL>https://github.com/johndoe</URL>
  </Document>
</ReferenceTo>
```

## 3. Country Codes (ISO 3166-1 alpha-2)

Common codes:
- NL: Netherlands
- BE: Belgium
- DE: Germany
- FR: France
- GB: United Kingdom
- US: United States
- ...

## 4. Language Codes (ISO 639-1)

Common codes:
- nl: Dutch
- en: English
- de: German
- fr: French
- es: Spanish
- it: Italian
- pt: Portuguese
- ...

## 5. Date Format

Dates in Europass use a specific format:
- **Year**: 2024
- **Month**: --06 (leading --)
- **Day**: ---15 (leading ---)

Example:
```xml
<Date>
  <Year>2024</Year>
  <Month>--06</Month>
  <Day>---15</Day>
</Date>
```

For year-only: `<Year>2024</Year>`
For year-month: 
```xml
<Year>2024</Year>
<Month>--06</Month>
```

## 6. Photo Format

Photos must be base64-encoded:

```xml
<Photo>
  <MimeType>image/jpeg</MimeType>
  <Data>iVBORw0KGgoAAAANSUhEUgAA...</Data>
</Photo>
```

Supported MIME types:
- image/jpeg
- image/png
- image/gif

Recommended:
- Format: JPEG
- Size: 300x400 pixels (portrait)
- File size: < 200 KB

## 7. Complete Example

See `examples/europass_example.xml` for a complete, valid Europass CV XML document.

## 8. JSON Representation

While Europass primarily uses XML, a JSON representation follows a similar structure:

```json
{
  "DocumentInfo": {
    "DocumentType": "ECV",
    "CreationDate": "2024-01-15T10:30:00Z",
    "XSDVersion": "V3.4",
    "Generator": "EuroCV"
  },
  "LearnerInfo": {
    "Identification": {
      "PersonName": {
        "FirstName": "John",
        "Surname": "Doe"
      },
      "ContactInfo": {
        "Email": {"Contact": "john.doe@example.com"}
      }
    },
    "WorkExperienceList": [...],
    "EducationList": [...],
    "Skills": {...}
  }
}
```

## References

- Official Europass Portal: https://europa.eu/europass
- Schema Documentation: https://interoperable.europe.eu/collection/europass
- ISCO-08 Codes: https://www.ilo.org/public/english/bureau/stat/isco/
- ISCED 2011: http://uis.unesco.org/en/topic/international-standard-classification-education-isced
- CEFR Levels: https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions

