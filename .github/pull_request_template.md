## 📝 Description

<!-- Provide a brief description of the changes in this PR -->

## 🎯 Type of Change

<!-- Please check the relevant option(s) -->

- [ ] 🐛 Bug fix (data correction, fixing incorrect information)
- [ ] ✨ New feature (adding new cities, states, or countries)
- [ ] 📝 Data update (updating existing information with more accurate data)
- [ ] 🔧 Build/Infrastructure (changes to scripts, workflows, or tooling)
- [ ] 📚 Documentation (updates to README, guides, or comments)
- [ ] 🗑️ Data removal (removing duplicate or invalid entries)

## 🌍 Affected Entities

<!-- List the countries, states, or cities affected by this change -->

- **Country/Countries**:
- **State(s)/Province(s)**:
- **City/Cities**:

## ✅ Checklist

<!-- Please check all that apply -->

- [ ] I have read the [CONTRIBUTING.md](../.github/CONTRIBUTING.md) guidelines
- [ ] I made changes to JSON files in the `contributions/` directory (preferred method)
- [ ] I have run `python3 bin/build_from_contributions.py` locally and it completed successfully
- [ ] My changes follow the existing data format and structure
- [ ] I have verified the data against reliable sources (WikiData, Wikipedia, official sources)
- [ ] For data corrections: I have provided sources/references below

## 📚 Sources & References

<!-- Provide links to WikiData, Wikipedia, or official sources that support your changes -->

-
-
-

## 🧪 Testing

<!-- Describe how you tested your changes -->

- [ ] Built the database locally from contributions
- [ ] Verified no build errors
- [ ] Checked data integrity (correct IDs, relationships, etc.)
- [ ] Tested in my application (if applicable)

## 📸 Screenshots/Evidence (Optional)

<!-- If applicable, add screenshots or evidence of the issue being fixed -->

## 💬 Additional Notes

<!-- Any additional information that reviewers should know -->

---

**Note for Reviewers**:
- ✅ Changes should be in `contributions/` directory JSON files
- ✅ New records should NOT have `id` field (auto-assigned during build)
- ✅ Verify sources are reliable and data is accurate
