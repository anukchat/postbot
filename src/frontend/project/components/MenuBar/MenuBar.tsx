import * as React from 'react';
import * as MenubarPrimitive from '@radix-ui/react-menubar';
import { Check, ChevronRight, Circle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useEditorStore } from '../../store/editorStore';

const MenuBar = React.forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof MenubarPrimitive.Root>>(
  ({ className, ...props }, ref) => (
    <MenubarPrimitive.Root
      ref={ref}
      className={cn(
        'flex h-9 items-center space-x-1 rounded-md bg-white p-1 dark:bg-gray-800',
        className
      )}
      {...props}
    />
  )
);
MenuBar.displayName = MenubarPrimitive.Root.displayName;

const MenuBarTrigger = React.forwardRef<HTMLButtonElement, React.ComponentPropsWithoutRef<typeof MenubarPrimitive.Trigger>>(
  ({ className, ...props }, ref) => (
    <MenubarPrimitive.Trigger
      ref={ref}
      className={cn(
        'flex cursor-default select-none items-center rounded-sm px-3 py-1 text-sm font-medium outline-none hover:bg-gray-100 focus:bg-gray-100 dark:hover:bg-gray-700',
        className
      )}
      {...props}
    />
  )
);
MenuBarTrigger.displayName = MenubarPrimitive.Trigger.displayName;

const MenuBarContent = React.forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof MenubarPrimitive.Content>>(
  ({ className, align = 'start', alignOffset = -4, sideOffset = 8, ...props }, ref) => (
    <MenubarPrimitive.Portal>
      <MenubarPrimitive.Content
        ref={ref}
        align={align}
        alignOffset={alignOffset}
        sideOffset={sideOffset}
        className={cn(
          'z-50 min-w-[12rem] overflow-hidden rounded-md border bg-white p-1 shadow-md animate-in slide-in-from-top-1 dark:bg-gray-800',
          className
        )}
        {...props}
      />
    </MenubarPrimitive.Portal>
  )
);
MenuBarContent.displayName = MenubarPrimitive.Content.displayName;

const MenuBarItem = React.forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof MenubarPrimitive.Item> & { inset?: boolean }>(
  ({ className, inset, ...props }, ref) => (
    <MenubarPrimitive.Item
      ref={ref}
      className={cn(
        'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-gray-100 focus:text-gray-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50 dark:focus:bg-gray-700',
        inset && 'pl-8',
        className
      )}
      {...props}
    />
  )
);
MenuBarItem.displayName = MenubarPrimitive.Item.displayName;

const MenuBarLabel = React.forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof MenubarPrimitive.Label> & { inset?: boolean }>(
  ({ className, inset, ...props }, ref) => (
    <MenubarPrimitive.Label
      ref={ref}
      className={cn(
        'px-2 py-1.5 text-sm font-semibold',
        inset && 'pl-8',
        className
      )}
      {...props}
    />
  )
);
MenuBarLabel.displayName = MenubarPrimitive.Label.displayName;

const MenuBarSeparator = React.forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof MenubarPrimitive.Separator>>(
  ({ className, ...props }, ref) => (
    <MenubarPrimitive.Separator
      ref={ref}
      className={cn('-mx-1 my-1 h-px bg-gray-100 dark:bg-gray-700', className)}
      {...props}
    />
  )
);
MenuBarSeparator.displayName = MenubarPrimitive.Separator.displayName;

export const MainMenuBar = () => {
  const { savePost, currentPost, downloadMarkdown } = useEditorStore();

  return (
    <MenuBar className="px-2 border-b rounded-none w-full">
      <MenubarPrimitive.Menu>
        <MenuBarTrigger>File</MenuBarTrigger>
        <MenuBarContent>
          <MenuBarItem onSelect={() => savePost()}>
            Save
            <span className="ml-auto text-xs text-gray-500">⌘S</span>
          </MenuBarItem>
          <MenuBarItem onSelect={() => downloadMarkdown()}>
            Download Markdown
            <span className="ml-auto text-xs text-gray-500">⌘D</span>
          </MenuBarItem>
        </MenuBarContent>
      </MenubarPrimitive.Menu>

      <MenubarPrimitive.Menu>
        <MenuBarTrigger>Edit</MenuBarTrigger>
        <MenuBarContent>
          <MenuBarItem>
            Undo
            <span className="ml-auto text-xs text-gray-500">⌘Z</span>
          </MenuBarItem>
          <MenuBarItem>
            Redo
            <span className="ml-auto text-xs text-gray-500">⌘Y</span>
          </MenuBarItem>
        </MenuBarContent>
      </MenubarPrimitive.Menu>

      <MenubarPrimitive.Menu>
        <MenuBarTrigger>View</MenuBarTrigger>
        <MenuBarContent>
          <MenuBarItem>
            Toggle Preview
            <span className="ml-auto text-xs text-gray-500">⌘P</span>
          </MenuBarItem>
          <MenuBarSeparator />
          <MenuBarItem>
            Full Screen
            <span className="ml-auto text-xs text-gray-500">F11</span>
          </MenuBarItem>
        </MenuBarContent>
      </MenubarPrimitive.Menu>
    </MenuBar>
  );
};

export {
  MenuBar,
  MenuBarTrigger,
  MenuBarContent,
  MenuBarItem,
  MenuBarSeparator,
  MenuBarLabel,
};
