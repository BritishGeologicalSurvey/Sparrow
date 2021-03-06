import {render} from 'react-dom'
import h from 'react-hyperscript'

import '../../frontend/shared/ui-init'
import {SiteTitle} from '../../frontend/shared/util'
import {DetritalZirconComponent} from './main'

MainPage = ->
  h 'div', [
    h SiteTitle, {subPage: 'Detrital zircon samples'}
    h DetritalZirconComponent
  ]

el = document.querySelector("#container")
render(h(MainPage), el)
