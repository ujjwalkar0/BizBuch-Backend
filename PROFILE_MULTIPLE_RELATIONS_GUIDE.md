# Profile API - Multiple Locations, Education & Work Experience Update

## Summary of Changes

You now have a fully normalized, flexible profile system supporting multiple education records and work experience entries. All data is properly mapped through relationships in the database.

## Models Structure

### 1. Profile Model (Parent)
- Stores basic profile information
- Has relationships to Location, Education, and WorkExperience models

### 2. ProfileLocation Model
Stores multiple locations for a user:
```python
Fields:
- location: CharField(255)           # e.g., "San Francisco, CA"
- is_primary: BooleanField          # Current location marker
- location_type: CharField           # Options: current, previous, hometown, other
- created_at: DateTimeField
- updated_at: DateTimeField

Related to: Profile (ForeignKey, related_name="locations")
Ordering: By is_primary (desc), then by creation date
```

### 3. ProfileEducation Model
Stores multiple education records:
```python
Fields:
- name: CharField(255)               # School/University name
- degrees: JSONField                 # Array of degrees (e.g., ["BS", "MS"])
- duration: CharField(100)           # e.g., "2015-2019" or "2015-Present"
- start_year: IntegerField
- end_year: IntegerField (nullable)
- is_current: BooleanField          # Currently studying?
- school_logo: ImageField           # School logo/badge
- description: TextField            # Additional details
- created_at: DateTimeField
- updated_at: DateTimeField

Related to: Profile (ForeignKey, related_name="educations")
Ordering: By is_current (desc), then by end_year (desc)
```

### 4. ProfileWorkExperience Model (NEW)
Stores multiple work experience records:
```python
Fields:
- company_name: CharField(255)
- job_title: CharField(255)
- location: CharField(255, nullable)
- employment_type: CharField        # full-time, part-time, freelance, internship, etc.
- start_year: IntegerField
- start_month: IntegerField(1-12, nullable)
- end_year: IntegerField(nullable)
- end_month: IntegerField(1-12, nullable)
- is_current: BooleanField          # Currently employed here?
- company_logo: ImageField
- description: TextField            # Job responsibilities & achievements
- skills: JSONField                 # Array of skills used in this role
- created_at: DateTimeField
- updated_at: DateTimeField

Related to: Profile (ForeignKey, related_name="work_experiences")
Ordering: By is_current (desc), then by end_year (desc)
```

## API Response Structure

### Complete Profile Response Example

```json
{
  "id": 1,
  "display_name": "John Doe",
  "username": "johndoe",
  "bio": "Passionate engineer",
  "avatar": "https://...",
  
  "headline": "Senior Engineer at Google",
  "current_position": "Senior Engineer",
  "company": "Google",
  "company_logo": "https://...",
  "industry": "Technology",
  
  "locations": [
    {
      "id": 1,
      "location": "San Francisco, CA",
      "is_primary": true,
      "location_type": "current",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "location": "New York, NY",
      "is_primary": false,
      "location_type": "previous",
      "created_at": "2023-06-20T14:45:00Z",
      "updated_at": "2023-06-20T14:45:00Z"
    }
  ],
  
  "email": "john@example.com",
  "phone": "+1-415-555-0123",
  "website": "https://johndoe.dev",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "twitter_url": "https://twitter.com/johndoe",
  
  "connections_count": 250,
  "followers_count": 150,
  "following_count": 100,
  "posts_count": 42,
  
  "is_connected": true,
  "is_following": true,
  "mutual_connections_count": 12,
  
  "is_verified": true,
  "is_premium": false,
  "account_type": "personal",
  
  "cover_image": "https://...",
  "joined_date": "2024-01-15T10:30:00Z",
  "skills": ["Python", "Django", "React"],
  
  "educations": [
    {
      "id": 1,
      "name": "Stanford University",
      "degrees": ["Bachelor of Science", "Master of Engineering"],
      "duration": "2015-2020",
      "start_year": 2015,
      "end_year": 2020,
      "is_current": false,
      "school_logo": "https://...",
      "description": "Computer Science major",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "MIT",
      "degrees": ["PhD"],
      "duration": "2020-Present",
      "start_year": 2020,
      "end_year": null,
      "is_current": true,
      "school_logo": "https://...",
      "description": "Pursuing PhD in Artificial Intelligence",
      "created_at": "2024-06-01T08:00:00Z",
      "updated_at": "2024-06-01T08:00:00Z"
    }
  ],
  
  "work_experiences": [
    {
      "id": 1,
      "company_name": "Google",
      "job_title": "Senior Software Engineer",
      "location": "Mountain View, CA",
      "employment_type": "full-time",
      "start_year": 2020,
      "start_month": 6,
      "end_year": null,
      "end_month": null,
      "is_current": true,
      "company_logo": "https://...",
      "description": "Led infrastructure team for payment systems. Improved latency by 40%.",
      "skills": ["Python", "Go", "Kubernetes", "AWS"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "company_name": "Meta",
      "job_title": "Software Engineer",
      "location": "Menlo Park, CA",
      "employment_type": "full-time",
      "start_year": 2018,
      "start_month": 7,
      "end_year": 2020,
      "end_month": 6,
      "is_current": false,
      "company_logo": "https://...",
      "description": "Built recommendation system serving 2B+ users.",
      "skills": ["Python", "C++", "React", "GraphQL"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 3,
      "company_name": "Microsoft",
      "job_title": "Intern",
      "location": "Seattle, WA",
      "employment_type": "internship",
      "start_year": 2017,
      "start_month": 6,
      "end_year": 2017,
      "end_month": 8,
      "is_current": false,
      "company_logo": "https://...",
      "description": "Internship during summer. Worked on cloud infrastructure.",
      "skills": ["C#", "Azure", ".NET"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  
  "open_to_work": true,
  "open_to_hire": false
}
```

## Update Endpoints - Request Format

### Update Profile with Locations, Education, and Work Experience

**Endpoint:** `PATCH /api/profiles/me/`

```json
{
  "display_name": "John Doe",
  "headline": "Senior Engineer",
  
  "locations": [
    {
      "location": "San Francisco, CA",
      "is_primary": true,
      "location_type": "current"
    },
    {
      "location": "Austin, TX",
      "is_primary": false,
      "location_type": "previous"
    }
  ],
  
  "educations": [
    {
      "name": "Stanford University",
      "degrees": ["BS Computer Science", "MS Engineering"],
      "duration": "2015-2020",
      "start_year": 2015,
      "end_year": 2020,
      "is_current": false,
      "description": "Computer Science major"
    }
  ],
  
  "work_experiences": [
    {
      "company_name": "Google",
      "job_title": "Senior Software Engineer",
      "location": "Mountain View, CA",
      "employment_type": "full-time",
      "start_year": 2020,
      "start_month": 6,
      "is_current": true,
      "description": "Led infrastructure team",
      "skills": ["Python", "Go", "Kubernetes"]
    }
  ],
  
  "skills": ["Python", "Django", "React"],
  "phone": "+1-415-555-0123",
  "website": "https://johndoe.dev",
  "open_to_work": true
}
```

## Files Changed

### Models
- ✅ `accounts/models/user.py` - Already updated
- ✅ `profiles/models/profile.py` - Updated with ProfileLocation, ProfileEducation, ProfileWorkExperience
- ✅ `profiles/models/__init__.py` - Added exports for new models

### Serializers
- ✅ `profiles/serializers/profile_location_serializer.py` - Updated with all three serializers
- ✅ `profiles/serializers/profile_serializer.py` - Updated to use relationships
- ✅ `profiles/serializers/profile_detail_response_serializer.py` - Updated to use relationships
- ✅ `profiles/serializers/profile_update_serializer.py` - Updated with work experience handling
- ✅ `profiles/serializers/profile_compact_serializer.py` - Unchanged (lightweight)
- ✅ `profiles/serializers/__init__.py` - Added ProfileWorkExperienceSerializer export

### Services
- ✅ `profiles/services/profile_stats_service.py` - No changes needed

### Views
- ✅ All views work unchanged with new serializers

## Database Migration Steps

```bash
# Create migrations for new models
python manage.py makemigrations accounts
python manage.py makemigrations profiles

# Review migrations before applying
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Create admin interface (optional)
python manage.py shell
# Then register models in admin.py
```

## Admin Registration Example

```python
# In profiles/admin.py
from django.contrib import admin
from profiles.models import Profile, ProfileLocation, ProfileEducation, ProfileWorkExperience

class ProfileLocationInline(admin.TabularInline):
    model = ProfileLocation
    extra = 1

class ProfileEducationInline(admin.TabularInline):
    model = ProfileEducation
    extra = 1

class ProfileWorkExperienceInline(admin.TabularInline):
    model = ProfileWorkExperience
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfileLocationInline, ProfileEducationInline, ProfileWorkExperienceInline]
    list_display = ['display_name', 'user', 'is_public', 'created_at']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileLocation)
admin.site.register(ProfileEducation)
admin.site.register(ProfileWorkExperience)
```

## Key Features

✅ **Multiple Locations** - Support current, previous, hometown, and other locations  
✅ **Flexible Education** - Store multiple degrees per institution  
✅ **Work Experience** - Complete employment history with skills & achievements  
✅ **Month-Level Precision** - Track employment and education down to the month  
✅ **Status Tracking** - Mark current roles and studies with `is_current` field  
✅ **Rich Media** - Support logos for schools and companies  
✅ **SOLID Architecture** - Separate serializers for each concern  
✅ **Proper Relationships** - All data normalized with ForeignKeys  
✅ **Ordered Results** - Current items appear first (automatically ordered)  
✅ **Indexed Queries** - Fast lookups on profile + is_current combination  

## Performance Considerations

### Query Optimization
```python
# Use select_related for single objects
user = User.objects.select_related('profile').get(pk=1)

# Use prefetch_related for related objects (multiple)
user = User.objects.prefetch_related(
    'profile__locations',
    'profile__educations',
    'profile__work_experiences'
).get(pk=1)
```

### Caching Strategy
```python
# Cache profile data for 5 minutes
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def get_profile(request, user_id):
    # Response cached for 5 minutes
```

## Frontend Integration Example

```typescript
interface ProfileResponse {
  locations: Array<{
    id: number;
    location: string;
    is_primary: boolean;
    location_type: 'current' | 'previous' | 'hometown' | 'other';
  }>;
  
  educations: Array<{
    id: number;
    name: string;
    degrees: string[];
    duration: string;
    start_year: number;
    end_year?: number;
    is_current: boolean;
    school_logo?: string;
    description: string;
  }>;
  
  work_experiences: Array<{
    id: number;
    company_name: string;
    job_title: string;
    location?: string;
    employment_type: string;
    start_year: number;
    start_month?: number;
    end_year?: number;
    end_month?: number;
    is_current: boolean;
    company_logo?: string;
    description: string;
    skills: string[];
  }>;
}

// Display education timeline
const EducationTimeline = ({ educations }: { educations: ProfileResponse['educations'] }) => {
  return (
    <div className="timeline">
      {educations.map(edu => (
        <div key={edu.id} className="timeline-item">
          {edu.school_logo && <img src={edu.school_logo} alt={edu.name} />}
          <h4>{edu.name}</h4>
          <p>{edu.degrees.join(', ')}</p>
          <p>{edu.duration}</p>
          {edu.is_current && <span className="badge">Currently studying</span>}
        </div>
      ))}
    </div>
  );
};

// Display work experience
const WorkTimeline = ({ experiences }: { experiences: ProfileResponse['work_experiences'] }) => {
  return (
    <div className="timeline">
      {experiences.map(exp => (
        <div key={exp.id} className="timeline-item">
          {exp.company_logo && <img src={exp.company_logo} alt={exp.company_name} />}
          <h4>{exp.job_title}</h4>
          <p className="company">{exp.company_name}</p>
          <p className="duration">{exp.start_year}/{exp.start_month || 'Jan'} - {exp.is_current ? 'Present' : `${exp.end_year}/${exp.end_month || 'Jan'}`}</p>
          {exp.location && <p className="location">{exp.location}</p>}
          <p className="type">{exp.employment_type}</p>
          {exp.description && <p className="description">{exp.description}</p>}
          {exp.skills.length > 0 && (
            <div className="skills">
              {exp.skills.map(skill => <span key={skill} className="skill-tag">{skill}</span>)}
            </div>
          )}
          {exp.is_current && <span className="badge">Current role</span>}
        </div>
      ))}
    </div>
  );
};
```

## Validation Rules

| Field | Validation |
|-------|-----------|
| location | Max 255 characters |
| location_type | Must be: current, previous, hometown, other |
| is_primary | Boolean |
| name (education) | Max 255 characters |
| degrees | Array of strings |
| duration | Max 100 characters |
| start_year | Integer (e.g., 2020) |
| end_year | Integer, nullable |
| school_logo | Image file |
| company_name | Max 255 characters |
| job_title | Max 255 characters |
| employment_type | One of: full-time, part-time, self-employed, freelance, contract, internship, apprenticeship, seasonal |
| company_logo | Image file |
| skills | Array of strings |

---

**Status**: ✅ Implementation Complete - Ready for database migration
