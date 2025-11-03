import {
  Button,
  ButtonGroup,
  Code,
  Spinner,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { FaEye } from "react-icons/fa"
import React from "react"
import {
  type ApiError,
  type TacacsConfigPublic,
  type TacacsConfigUpdate,
  TacacsConfigsService,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"

interface ShowTacacsConfigProps {
  tacacs_config: TacacsConfigPublic
  children?: React.ReactNode
}

const ShowTacacsConfig = ({
  tacacs_config,
  children,
}: ShowTacacsConfigProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (data: TacacsConfigUpdate) =>
      TacacsConfigsService.updateTacacsConfig({
        id: tacacs_config.id,
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast("TacacsConfig activated successfully.")
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tacacs_configs"] })
    },
  })

  const { data, isLoading, error } = useQuery({
    queryKey: ["tacacs_config", tacacs_config.id],
    queryFn: () => TacacsConfigsService.readTacacsConfigById({ id: tacacs_config.id }),
    enabled: isOpen, // Only fetch when the dialog is open
  })

  const onActivate = () => {
    // We only need to send the filename, as the backend will handle the activation logic.
    // The description is optional.
    const { filename, description } = tacacs_config
    mutation.mutate({ filename, description })
  }

  const renderContent = () => {
    if (isLoading) {
      return <Spinner />
    }
    if (error) {
      return <Text color="red.500">Error loading configuration.</Text>
    }
    if (data?.data) {
      return (
        <Textarea
          readOnly
          value={data.data}
          rows={20}
          fontFamily="monospace"
        />
      )
    }
    return <Text>No content available.</Text>
  }

  return (
    <DialogRoot
      size={{ base: "md", md: "xl" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        {children || (
          <Button variant="ghost">
            <FaEye fontSize="16px" />
            Show Config
          </Button>
        )}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Configuration for: <Code>{tacacs_config.filename}</Code>
          </DialogTitle>
        </DialogHeader>
        <DialogBody>
          <VStack gap={4} align="stretch">
            {renderContent()}
          </VStack>
        </DialogBody>
        <DialogFooter gap={2}>
          <ButtonGroup>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={mutation.isPending}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              onClick={onActivate}
              loading={mutation.isPending}
              disabled={tacacs_config.active}
            >
              {tacacs_config.active ? "Already Active" : "Activate"}
            </Button>
          </ButtonGroup>
        </DialogFooter>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default ShowTacacsConfig
