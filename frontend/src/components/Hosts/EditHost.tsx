import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type HostPublic, HostsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditHostProps {
  host: HostPublic
}

interface HostUpdateForm {
  name: string
  ipv4_address: string
  secret_key: string
  description?: string
}



const EditHost = ({ host }: EditHostProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<HostUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...host,
      name: host.name ?? undefined,
      ipv4_address: host.ipv4_address ?? undefined,
      secret_key: host.secret_key ?? undefined,
      description: host.description ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: HostUpdateForm) =>
      HostsService.updateHost({ id: host.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Host updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["hosts"] })
    },
  })

  const onSubmit: SubmitHandler<HostUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit Host
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit Host</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the item details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="name"
              >
                <Input
                  {...register("name", {
                    required: "Title is required",
                  })}
                  placeholder="name"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.ipv4_address}
                errorText={errors.ipv4_address?.message}
                label="ipv4_address"
              >
                <Input
                  {...register("ipv4_address", {
                    required: "ipv4_address is required.",
                  })}
                  placeholder="ipv4_address"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.secret_key}
                errorText={errors.secret_key?.message}
                label="secret_key"
              >
                <Input
                  {...register("secret_key", {
                    required: "secret_key is required.",
                  })}
                  placeholder="secret_key"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditHost
