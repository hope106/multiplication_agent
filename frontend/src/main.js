import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/main.css'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(ElementPlus)

app.mount('#app') 