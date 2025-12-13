'use client'

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
} from '@/components/ui/sidebar'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { DualRangeSlider } from './ui/dual-range-slider'
import { useSearch, ColorFilter, PriceRange } from '@/contexts/search-context'

const COLOR_OPTIONS: { value: ColorFilter; bgClass: string }[] = [
  { value: 'black', bgClass: 'bg-black' },
  { value: 'white', bgClass: 'bg-white' },
  { value: 'gray', bgClass: 'bg-gray-400' },
  { value: 'red', bgClass: 'bg-red-400' },
  { value: 'green', bgClass: 'bg-green-400' },
  { value: 'blue', bgClass: 'bg-blue-400' },
  { value: 'yellow', bgClass: 'bg-yellow-400' },
  { value: 'purple', bgClass: 'bg-purple-400' },
  { value: 'pink', bgClass: 'bg-pink-400' },
]

export function AppSidebar() {
  const { filters, updateFilter, resetFilters } = useSearch()

  // check if any filters are active (different from defaults)
  const hasActiveFilters =
    filters.color !== undefined ||
    filters.gender !== 'all' ||
    filters.price[0] !== 0 ||
    filters.price[1] !== 2500

  return (
    <Sidebar>
      <SidebarHeader />
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Color</SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="grid grid-cols-2 gap-1 mx-auto ml-2">
              {COLOR_OPTIONS.map(({ value, bgClass }) => (
                <button
                  key={value}
                  onClick={() =>
                    updateFilter(
                      'color',
                      filters.color === value ? undefined : value
                    )
                  }
                  className={cn(
                    'flex flex-row items-center gap-2 p-1 rounded hover:bg-bg-zinc-200 transition-colors',
                    filters.color === value && 'bg-zinc-200'
                  )}
                >
                  <div className={cn('w-6 h-6 border rounded-md', bgClass)} />
                  <span className="capitalize">{value}</span>
                </button>
              ))}
            </div>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Gender</SidebarGroupLabel>
          <SidebarGroupContent>
            <RadioGroup
              value={filters.gender}
              onValueChange={(value) =>
                updateFilter('gender', value as typeof filters.gender)
              }
              className="ml-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="mens" id="mens" />
                <Label htmlFor="mens">Mens</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="womens" id="womens" />
                <Label htmlFor="womens">Womens</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="all" id="all" />
                <Label htmlFor="all">All</Label>
              </div>
            </RadioGroup>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Price</SidebarGroupLabel>
          <SidebarGroupContent>
            <DualRangeSlider
              className="mt-8 mx-2 w-11/12"
              label={(value) => <span>${value}</span>}
              value={filters.price}
              onValueChange={(value) =>
                updateFilter('price', value as PriceRange)
              }
              min={0}
              max={2500}
              step={5}
            />
          </SidebarGroupContent>
        </SidebarGroup>
        {hasActiveFilters && (
          <div className="px-4 mt-4">
            <Button
              variant="outline"
              onClick={resetFilters}
              className="w-full"
              size="sm"
            >
              Clear Filters
            </Button>
          </div>
        )}
      </SidebarContent>
      <SidebarFooter />
    </Sidebar>
  )
}
