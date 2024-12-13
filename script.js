document.addEventListener('DOMContentLoaded', () => {
    let repositories = [];

    // Загрузка JSON с проектами
    fetch('github_projects.json')
        .then(response => response.json())
        .then(data => {
            repositories = data.repository;
            displayProjects(repositories);
        })
        .catch(error => {
            console.error('Ошибка при загрузке JSON:', error);
        });

    // Отображение проектов
    function displayProjects(repos) {
        const projectList = document.getElementById('project-list');
        projectList.innerHTML = '';
    
        repos.forEach(repo => {
            const projectDiv = document.createElement('div');
            projectDiv.classList.add('project');
    
            const projectTitle = document.createElement('h2');
            const projectLink = document.createElement('a');
            projectLink.href = repo.url;
            projectLink.textContent = repo.name;
            projectLink.target = '_blank';
            projectTitle.appendChild(projectLink);
            projectDiv.appendChild(projectTitle);
    
            const projectDate = document.createElement('p');
            projectDate.classList.add('project-date');
            const createdAt = new Date(repo.created_at).toLocaleDateString();
            projectDate.textContent = `Created on: ${createdAt}`;
            projectDiv.appendChild(projectDate);
    
            const projectDescription = document.createElement('p');
            projectDescription.classList.add('project-description');
            projectDescription.textContent = repo.description || 'No description available';
            projectDiv.appendChild(projectDescription);
    
            if (repo.issues_with_links.length > 0 || repo.issues_without_links.length > 0) {
                const issuesContainer = document.createElement('div');
                issuesContainer.classList.add('issues-container');
    
                const allIssues = [...repo.issues_with_links, ...repo.issues_without_links];
                const maxIssuesToShow = 5;
    
                allIssues.slice(0, maxIssuesToShow).forEach(issue => {
                    const issueDiv = createIssueDiv(issue);
                    issuesContainer.appendChild(issueDiv);
                });
    
                if (allIssues.length > maxIssuesToShow) {
                    const toggleButton = document.createElement('button');
                    toggleButton.textContent = 'Show More';
                    toggleButton.classList.add('toggle-button');
                    toggleButton.addEventListener('click', () => {
                        if (toggleButton.textContent === 'Show More') {
                            allIssues.slice(maxIssuesToShow).forEach(issue => {
                                const issueDiv = createIssueDiv(issue);
                                issuesContainer.appendChild(issueDiv);
                            });
                            toggleButton.textContent = 'Show Less';
                        } else {
                            while (issuesContainer.childNodes.length > maxIssuesToShow) {
                                issuesContainer.removeChild(issuesContainer.lastChild);
                            }
                            toggleButton.textContent = 'Show More';
                        }
                    });
                    projectDiv.appendChild(toggleButton);
                }
    
                projectDiv.appendChild(issuesContainer);
            }
    
            projectList.appendChild(projectDiv);
        });
    }
    
    function createIssueDiv(issue) {
        const issueDiv = document.createElement('div');
        issueDiv.classList.add('issue');
    
        const issueTitle = document.createElement('p');
        issueTitle.classList.add('issue-title');
        issueTitle.textContent = issue.title || 'No title';
        issueDiv.appendChild(issueTitle);
    
        if (issue.links && issue.links.length > 0) {
            const linksContainer = document.createElement('div');
            linksContainer.classList.add('issue-links');
            issue.links.forEach(link => {
                const linkElement = document.createElement('a');
                linkElement.href = link.url;
                linkElement.textContent = link.text;
                linkElement.target = '_blank';
                linksContainer.appendChild(linkElement);
            });
            issueDiv.appendChild(linksContainer);
        } else if (issue.description) {
            const description = document.createElement('p');
            description.textContent = issue.description;
            issueDiv.appendChild(description);
        }
    
        return issueDiv;
    }
    

    // Сортировка проектов
    function sortProjects(sortOrder) {
        if (sortOrder === 'date-newest') {
            repositories.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        } else if (sortOrder === 'date-oldest') {
            repositories.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        } else if (sortOrder === 'alphabetical-asc') {
            repositories.sort((a, b) => a.name.localeCompare(b.name));
        } else if (sortOrder === 'alphabetical-desc') {
            repositories.sort((a, b) => b.name.localeCompare(a.name));
        }
        displayProjects(repositories);
    }

    // Поиск проектов
    function searchProjects(query) {
        const filteredRepos = repositories.filter(repo => {
            const nameMatch = repo.name.toLowerCase().includes(query.toLowerCase());
            const descriptionMatch = repo.description && repo.description.toLowerCase().includes(query.toLowerCase());
            return nameMatch || descriptionMatch;
        });
        displayProjects(filteredRepos);
    }

    // Обработчики событий для сортировки и поиска
    document.getElementById('sort').addEventListener('change', (event) => {
        sortProjects(event.target.value);
    });

    document.getElementById('search').addEventListener('input', (event) => {
        searchProjects(event.target.value);
    });
});
