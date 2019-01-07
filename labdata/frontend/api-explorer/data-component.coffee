import {Component} from 'react'
import h from 'react-hyperscript'
import {CollapsePanel} from './collapse-panel'

class APIDataComponent extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props

  render: ->
    {data} = @props
    # Just as a shorthand, there will be no results unless
    # there are arguments for any given route
    return null unless data.arguments?
    h CollapsePanel, {className: 'data', title: 'Data'}, [
      h 'div', 'Data'
    ]

export {APIDataComponent}