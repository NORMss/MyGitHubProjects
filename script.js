document.addEventListener('DOMContentLoaded', () => {
    let repositories = [];

    // Функция для загрузки JSON с проектами
    fetch('github_projects.json')
        .then(response => response.json())
        .then(data => {
            repositories = data.repository;
            displayProjects(repositories);
        })
        .catch(error => {
            console.error('Ошибка при загрузке JSON:', error);
        });

    // Функция для отображения проектов
    function displayProjects(repos) {
        const projectList = document.getElementById('project-list');
        projectList.innerHTML = '';  // Очищаем старые проекты

        repos.forEach(repo => {
            const projectDiv = document.createElement('div');
            projectDiv.classList.add('project');

            const projectTitle = document.createElement('h2');
            const projectLink = document.createElement('a');
            projectLink.href = repo.url;
            projectLink.textContent = repo.name;
            projectLink.target = '_blank'; // Открыть ссылку в новом окне
            projectTitle.appendChild(projectLink);
            projectDiv.appendChild(projectTitle);

            // Отображение даты создания репозитория
            const projectDate = document.createElement('p');
            projectDate.classList.add('project-date');
            const createdAt = new Date(repo.created_at).toLocaleDateString(); // Форматируем дату
            projectDate.textContent = `Created on: ${createdAt}`;
            projectDiv.appendChild(projectDate);

            const projectDescription = document.createElement('p');
            projectDescription.classList.add('project-description');
            projectDescription.textContent = repo.description || 'No description available';
            projectDiv.appendChild(projectDescription);

            // Сортируем уроки по возрастанию
            repo.issues.sort((a, b) => a.title.localeCompare(b.title));

            // Если у проекта есть issues с ссылками
            repo.issues.forEach(issue => {
                const issueDiv = document.createElement('div');
                issueDiv.classList.add('issue');

                const issueTitle = document.createElement('p');
                issueTitle.classList.add('issue-title');
                issueTitle.textContent = issue.title;
                issueDiv.appendChild(issueTitle);

                const issueLinks = document.createElement('div');
                issueLinks.classList.add('issue-links');

                // Проходим по каждой ссылке в issue
                issue.links.forEach(link => {
                    const issueLink = document.createElement('a');
                    issueLink.href = link.url;
                    issueLink.textContent = link.text;
                    issueLink.target = '_blank'; // Открытие ссылки в новом окне
                    issueLinks.appendChild(issueLink);
                });

                issueDiv.appendChild(issueLinks);
                projectDiv.appendChild(issueDiv);
            });

            projectList.appendChild(projectDiv);
        });
    }

    // Функция сортировки проектов по дате и алфавиту
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

    // Функция поиска по названию и описанию проекта
    function searchProjects(query) {
        const filteredRepos = repositories.filter(repo => {
            const nameMatch = repo.name.toLowerCase().includes(query.toLowerCase());
            const descriptionMatch = repo.description && repo.description.toLowerCase().includes(query.toLowerCase());
            return nameMatch || descriptionMatch;
        });
        displayProjects(filteredRepos);
    }

    // Обработчик события сортировки
    document.getElementById('sort').addEventListener('change', (event) => {
        sortProjects(event.target.value);
    });

    // Обработчик события поиска
    document.getElementById('search').addEventListener('input', (event) => {
        searchProjects(event.target.value);
    });
});
