import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/home/HomePage.vue'
import AnnouncementManagement from '../components/announcement/AnnouncementManagement.vue'
import NotificationPage from '../components/notification/NotificationPage.vue'
import UserProfile from '../components/user/UserProfile.vue'
import CompetitionCategory from '../components/competition/CompetitionCategory.vue'
import CompetitionSpace from '../components/competition/CompetitionSpace.vue'
import TeamSpace from '../components/team/TeamSpace.vue'
import MyTeamsPage from '../components/team/MyTeamsPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/announcement',
    name: 'Announcement',
    component: AnnouncementManagement
  },
  {
    path: '/notification',
    name: 'Notification',
    component: NotificationPage
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/competition/category',
    name: 'CompetitionCategory',
    component: CompetitionCategory,
    meta: { title: '竞赛分类' }
  },
  {
    path: '/competition/space/:id',
    name: 'CompetitionSpace',
    component: CompetitionSpace,
    meta: { title: '竞赛空间' }
  },
  {
    path: '/competition/space/:spaceId/teams',
    name: 'TeamSpace',
    component: TeamSpace,
    meta: { title: '组队空间', requiresAuth: true },
    props: true
  },
  {
    path: '/my-teams',
    name: 'MyTeams',
    component: MyTeamsPage,
    meta: { title: '我的队伍', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router