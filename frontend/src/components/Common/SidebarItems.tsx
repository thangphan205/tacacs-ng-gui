import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink } from "@tanstack/react-router"
import { FiBriefcase, FiHome, FiSettings, FiUsers } from "react-icons/fi"
import type { IconType } from "react-icons/lib"

import type { UserPublic } from "@/client"

const items = [
  { icon: FiHome, title: "Dashboard", path: "/", level: 1 },
  { icon: FiBriefcase, title: "Items", path: "/items", level: 1 },
  { icon: FiBriefcase, title: "Hosts", path: "/hosts", level: 1 },
  { icon: FiBriefcase, title: "Tacacs Groups", path: "/tacacs_groups", level: 1 },
  { icon: FiBriefcase, title: "Tacacs Users", path: "/tacacs_users", level: 1 },
  { icon: FiBriefcase, title: "Tacacs Services", path: "/tacacs_services", level: 1 },
  { icon: FiBriefcase, title: "Profiles", path: "/profiles", level: 1 },
  { icon: FiBriefcase, title: "Profiles Script", path: "/profilescripts", level: 2 },
  { icon: FiBriefcase, title: "Profiles Script Set", path: "/profilescriptsets", level: 2 },
  { icon: FiBriefcase, title: "Rulesets", path: "/rulesets", level: 1 },
  { icon: FiBriefcase, title: "Rulesets Script", path: "/rulesetscripts", level: 2 },
  { icon: FiBriefcase, title: "Rulesets Script Set", path: "/rulesetscriptsets", level: 2 },
  { icon: FiSettings, title: "User Settings", path: "/settings", level: 1 },
]

interface SidebarItemsProps {
  onClose?: () => void
}

interface Item {
  icon: IconType
  title: string
  path: string
  level: number
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems: Item[] = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin", level: 1 }]
    : items

  const listItems = finalItems.map(({ icon, title, path, level }) => (
    <RouterLink key={title} to={path} onClick={onClose}>
      <Flex
        gap={4}
        px={level === 1 ? 4 : 8}
        py={2}
        _hover={{
          background: "gray.subtle",
        }}
        alignItems="center"
        fontSize="sm"
      >
        <Icon as={icon} alignSelf="center" />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ))

  return (
    <>
      <Text fontSize="xs" px={4} py={2} fontWeight="bold">
        Menu
      </Text>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
