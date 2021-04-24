// myEventEmitter.ts
import { EventEmitter as OriginalEventEmitter } from 'events'

// アクション一覧。必ずオーバーロードしている型と一致させること！！
type EventType = 'flash' | 'greeting'

export interface FlashAction {
  label: string
  onClick: () => void
}

class EventEmitter extends OriginalEventEmitter {
  // 使うアクションの型をオーバーロード
  public emit(
    event: 'flash',
    msg: string,
    action?: FlashAction,
  ): boolean
  public emit(event: 'greeting', name: string): boolean

  // メソッド本体。元々のemitメソッドを踏襲している
  public emit(event: EventType, ...args: any[]) {
    return super.emit(event, ...args)
  }
}


export const eventEmitter = new EventEmitter()