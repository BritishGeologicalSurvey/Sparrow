###
Basic functionality to bootstrap a single-page React webapp
###

import './shared/ui-init'
import {App} from './app'
import {createElement} from 'react'
import {render} from 'react-dom'

el = document.querySelector("#container")
render(createElement(App), el)
